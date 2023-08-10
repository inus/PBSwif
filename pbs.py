#pbs.py
SSH_TIMEOUT=15

try:
    import drmaa
    DRMAA_avail = True
except ImportError:
    print('No DRMAA, not a submit host')
    DRMAA_avail = False

import datetime
import streamlit as st
from subprocess import run, TimeoutExpired
import os,socket
import inet
import tempfile

from common import show_info, check_select, copy_button
from shell import run_cluster_cmd
from sidebar import DEFAULT_WALLTIME

PBS_HOSTS = ['login1', 'login2', 'globus.chpc.ac.za']
host = socket.gethostname()
PBS_HOST=host in PBS_HOSTS
User_RPs = []


def show_pbs(st, pbs_tab):

        PBS_dict = {
            'bash': '#!/bin/bash', 'programme': 'P',
            'email': 'M', 'jobname': 'N', 'queue': 'q',
            'error': 'e', 'out': 'o', 'join': 'j oe',
            'Interactive' : 'I', 'Xfwd': 'X', 'Vars': 'V',}
        
        dl_file_contents=''

        @st.cache_data(persist="disk")
        def get_rp_detail(pgms):
            prm = '|'.join(pgms)

            cmd = "cat /home/userdb/projects_status.csv | grep -E \'" + prm + "\'"
            if not DRMAA_avail:
                cmd =  "ssh " + st.session_state.user + '@' + st.session_state.server + ' ' +cmd
            
            op = run(cmd, capture_output=True, shell=True, timeout=SSH_TIMEOUT, check=True)

            if op.stdout is not None:
                lines = op.stdout.decode().splitlines()                
                rp_list=[]
                rp_list += [ l.split(',') for l in lines]
                pgm_dict = {}
                for line in rp_list:
                    for  pgm in pgms:
                        if pgm == line[0]:
                            pgm_dict[pgm] = {'start': line[1], 'end': line[2],
                                        'alloc': line[3], 'cpuh': line[4]}                             
                return pgm_dict
#To do:  convert above to form   # >>> {k:row[0] for row in groups for k in row[1:]}


        @st.cache_data(persist="disk")
        def get_rp_list(): # get list of matching programmes for user

            
#            op=run_cluster_cmd(st.session_state.user + '@' + st.session_state.server,
#                {'rp': 'grep ' + st.session_state.user + ' /home/userdb/programme_info.csv'},'rp','') # fake cmd dict            

            cmd = 'grep ' + st.session_state.user.rstrip() + ' /home/userdb/programme_info.csv' 
            if not DRMAA_avail:
                cmd = 'ssh ' + st.session_state.user + '@' + st.session_state.server + ' ' + cmd 
#            else:
#            op = run( 'grep ' + st.session_state.user + ' /home/userdb/programme_info.csv',
#            import pdb; pdb.set_trace()
            op = run(cmd, capture_output=True, shell=True, timeout=SSH_TIMEOUT, check=True)
            pgms = []
            opl = op.stdout.decode().splitlines()
            for line in range(len(opl)):
                word = opl[line].split(',')[0]
                pgms.append(word)
            user_rps=get_rp_detail(pgms)
            return user_rps 
               
        def show_rp_info(rp_dict, place):                                
            def show_rp_data():
                with place.container():                    
                    stt = datetime.datetime.strptime(
                            rp_dict[st.session_state.user_rp]['start'], '%Y%m%d' )
                    st_d = stt.strftime('%-d %b %Y') 
                    st.info("Start: " +  st_d)
                    et = datetime.datetime.strptime(
                            rp_dict[st.session_state.user_rp]['end'], '%Y%m%d' )
                    et_d = et.strftime('%-d %b %Y') 
                    st.info('End:  ' + et_d )
                    st.info('CPU-h : ' + rp_dict[st.session_state.user_rp]['cpuh'] +
                                ' of ' + rp_dict[st.session_state.user_rp]['alloc'])
                if et < datetime.datetime.now():  
                    st.write('Expired :warning:')

            if 'user_rp' in st.session_state.keys():
                show_rp_data()
            

        def copy_pbs_file(file):
            filename='/tmp/' + file
            fp = open(filename, 'r')
            dl_file_contents=fp.read(); fp.close()
            #creds = st.session_state.user + '@' + st.session_state.server 
            st.info("Copying job file to " + st.session_state.workdir)
            CMD = 'cp ' + filename + ' '  + "${HOME}/" +  st.session_state.workdir + '/'                                    
            print("DEBUG copy  :", CMD)
            exitcode = run(CMD, capture_output=True, shell=True) 

            if exitcode.returncode < 0:
                st.error("Could not copy file to workdir, timeout " + filename + exitcode.returncode)
            else:   
                st.info('File ' + filename + ' copied to workdir ' + \
                        st.session_state.workdir + '/' + file)
            print("DEBUG : " , exitcode.stdout.decode())
            st.info(exitcode.stdout.decode())


        def send_pbs_file(file):
            filename='/tmp/' + file
            fp = open(filename, 'r')
            dl_file_contents=fp.read(); fp.close()
            creds = st.session_state.user + '@' + st.session_state.server 
            st.info("Copying job file via scp to " + st.session_state.server)
            CMD = 'scp ' + filename + ' ' + creds + ':' + st.session_state.workdir                                    
            exitcode = run(CMD, capture_output=True, shell=True) 

            if exitcode.returncode < 0:
                st.error("Could not copy file to server, timeout " + filename + exitcode.returncode)
            else:   
                st.info('File ' + filename + ' copied to cluster ' + \
                        st.session_state.workdir + '/' + file)
            

        def submit_pbs_file(file):
            creds = st.session_state.user + '@' + st.session_state.server 

            if  not DRMAA_avail:
                    qsub_out = run("ssh " + creds  + \
                        ' qsub ' + st.session_state.workdir \
                        + '/' + file, 
                        capture_output=True, shell=True)                                        
            else:
                    qsub_out = run( \
                        ' qsub ' + "${HOME}/" + st.session_state.workdir \
                        + '/' + file, 
                        capture_output=True, shell=True)                                        

            
            if qsub_out.returncode < 0:
                st.error("Timeout, Could not run qsub " + qsub_out.returncode)
                print("ERROR: Timeout, qsub command failed to send")
                return
            else:
                print("INFO: qsub command sent :", ' qsub ' + 
                st.session_state.workdir \
                + '/' + file ) 
                st.info('qsub command sent')
            if qsub_out.returncode == 0:
                jobid = qsub_out.stdout.decode()
                st.success('Job ' + str(jobid) + 'submitted')
                print("INFO: post qsub ", qsub_out.stdout.decode())


        def save_dl_file(cmd):
            dl_file_contents=''
            for k in cmd.keys():
                dl_file_contents += cmd[k] + '\n'
            #fname='/tmp/' + st.session_state.jobname + '.pbs'
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
                fp.write(dl_file_contents); 
            #fp.close()
            #st.info('File saved to ' + fname )


        def read_form():
            cmd={};qs_cmd={}
            checked=check_select()
            for k in PBS_dict:
                if k in st.session_state.keys():
                        if k=='bash':
                            if st.session_state[k]:
                                cmd[k] = PBS_dict[k]
                        elif k in ['jobname', 'email', 'programme']:
                            if st.session_state[k]:
                                qs_cmd[k] = '-' + PBS_dict[k] + ' ' + st.session_state[k] 
                                cmd[k] = '#PBS ' +  qs_cmd[k] 
                                if k=='email':
                                    qs_cmd['email_opts'] = '-m' + st.session_state.email_opts 
                                    cmd['email_opts'] = '#PBS -m ' + st.session_state.email_opts
                        elif k in [ 'join' , 'interactive', 'Xfwd',]:
                            if st.session_state[k]:
                                qs_cmd[k] = '-' + PBS_dict[k]
                                cmd[k] = '#PBS ' +  qs_cmd[k] 
                        else:
                            if st.session_state[k]:
                                if k=='queue':
                                    qs_cmd[k] =   '-' + PBS_dict[k] + ' ' + checked[k] 
                                    cmd[k] = '#PBS ' + qs_cmd[k]

            if checked['ngpus']:
                selstr =  '-l select={}:ncpus={}:mpiprocs={}:ngpus:{}:mem={}GB -l walltime={} '.format(
                    checked['nodect'], checked['ncpus'], checked['mpiprocs'], 
                    checked['ngpus'], checked['mem'], checked['walltime'],)

            else:
                selstr =  '-l select={}:ncpus={}:mpiprocs={}:mem={}GB -l walltime={} '.format(                    
                    checked['nodect'], checked['ncpus'], checked['mpiprocs'], checked['mem'], 
                    checked['walltime'],)
            
            qs_cmd['Select'] = selstr
            cmd['Select']  = '#PBS ' + selstr
            cmd['modules'] = st.session_state.modules
            cmd['command'] = st.session_state.command
            qs_cmd['command'] = st.session_state.command
            save_dl_file(cmd)
            return cmd, qs_cmd # returns both, latter for inline qsub, i.e. without #PBS prefix

        def setup_rp():
            leftcol1, centrecol1, rightcol1 = st.columns([1,1,1])
            with centrecol1:
                rp_info_place = st.empty() 
                getrp=st.checkbox("Get RP", key='getrp', help='(Re)Select RP code for programme info')
                if getrp:
                    User_RPs = get_rp_list()                    
                
            with rightcol1:
                rp_info_place2 = st.empty() 
                if st.session_state.getrp:
                    if not 'rp_dict' in locals() or 'rp_dict' in globals():
                        rp_dict = get_rp_list()

                    if rp_dict:
                        RP_selectbox_labels = rp_dict.keys() 
                        st.selectbox("CHPC Research Programme Code", 
                                        RP_selectbox_labels, key='user_rp',
                                        on_change=show_rp_info(
                                        rp_dict, rp_info_place),
                                        help="Select to see allocation") 
                    else:
                        RP_selectbox_labels = ''
                        st.selectbox("CHPC Research Programme Code", 
                                        RP_selectbox_labels, key='user_rp',
                                        on_change=show_rp_info(
                                        rp_dict, rp_info_place)) 
        def setup_form():
            form_leftcol, form_rightcol = st.columns([1,2])
            with form_leftcol:                        
                jobname = st.text_input("PBS job name", 
                            value='JobName', key="jobname", max_chars=15,)
                if st.session_state.getrp:
                    if st.session_state.user_rp == "":
                        msg = "**:red[CHPC Research Programme Code :warning:]**"
                    else:
                        msg = "CHPC Research Programme Code" 
                    programme = st.text_input(msg, placeholder='CHPC9999',
                                    key='programme', max_chars=8,
                                    help='Provide your CHPC allocated RP code',
                                    value = st.session_state.user_rp)
                email = st.text_input("Email address", placeholder='your@email.addr',
                                    key='email', help="Fill in to receive job notification email")                
                if st.session_state.email != "": # mail events abe
                    lcol1, ccol1, rcol1 = st.columns(3)                                    
                    with lcol1:mail_on_b = st.checkbox('b', key='mail_on_begin', help='Begin')
                    with ccol1:mail_on_e = st.checkbox('e', key='mail_on_end', help='End', value=True)
                    with rcol1:mail_on_a = st.checkbox('a', key='mail_on_abort', help='Abort')
                    if email:
                        email_opts = ''
                        if mail_on_a:  email_opts += 'a'
                        if mail_on_b:  email_opts += 'b'
                        if mail_on_e:  email_opts += 'e'
                        st.session_state['email_opts'] = email_opts

                col_left, col_right = st.columns([1,1])

                with col_left:
                    bash  = st.checkbox("Enable bash", key="bash", value=True,
                                    help="Add bash shell to script header")
                with col_right:
                    join  = st.checkbox("Join files", key="join", value=False,
                                    help="Combine output and error into one file")
            
            with form_rightcol:
                errorfile = st.text_input("Error file name", key='error',
                                        help='Leave empty for generated jobname.job-id')
                outfile = st.text_input("Output file name", key='out',
                                        help="Leave empty for generated jobname.job-id"  )
                workdir = st.text_input("Working directory", value = 'lustre', key='workdir', 
                                        help="Fill in to change directory to this")                     
                modules = st.text_area("Modules and initialization code", 
                                    placeholder="module load chpc/BIOMODULES python",
                                    key='modules', help="Any other initialization")
            command = st.text_input("Commandline", 
                                    placeholder="echo Hello from $(hostname) on $(date)", 
                                    key='command', help='Commands, switches and arguments')

            dl_filename = st.text_input("Script file name", key='dl_filename',
                                label_visibility='collapsed', 
                                value=st.session_state.jobname + '.pbs')         

        def submit_cli_qsub():

            if not ( 'pbs' in locals() or 'pbs' in globals() ):
                pbs = drmaa.Session()
                try:
                    pbs.initialize()
                except:
                    st.warning("Can not initialize PBS-DRMAA")
                    #return
            else:
                print("Debug: pbs not none, not initialized")

            cmds = get_cli_cmds()
            select = cmds['Select']

            if st.session_state.place != "none":
                select = select + " -l place={}".format(st.session_state.place)

            if st.session_state.walltime != DEFAULT_WALLTIME:
                select = select + " -l walltime=" + str(st.session_state.walltime) 

            jt = pbs.createJobTemplate()

            jt.remoteCommand = cmds['command']
            jt.jobName = st.session_state.jobname
            jt.workingDirectory = st.session_state.workdir

            if st.session_state.user_rp != "":
                jt.nativeSpecification = select + " -P " + st.session_state.user_rp 
            else:
                st.error("Can not run without a programme code")
                return

            if st.session_state.email != "":
                jt.email = st.session_state.email 

            try:
                jobid = pbs.runJob(jt)
                st.success('Job has been submitted to PBS, job id **[' + jobid + ']**')
            except:
                st.error( 'PBS job not submitted. Check if your RP programme code is valid')


        def submit_cli_qsub_ssh():

            cmds = get_cli_cmds()
            select = cmds['Select']
            if st.session_state.place != "none":
                select += " -l place={}".format(st.session_state.place)
            if st.session_state.walltime != DEFAULT_WALLTIME:
                select += " -l walltime=" + str(st.session_state.walltime) 
            if st.session_state.queue != "":
                select += " -q " + st.session_state.queue
            if st.session_state.user_rp != "":
                select += " -P " + st.session_state.user_rp 
            else:
                st.error("Can not run without a programme code")
                return
            if st.session_state.email != "":
                select += " -m " + st.session_state.email 
            if st.session_state.command != "":
                select += " -- " + st.session_state.command

            try:                    
                creds = st.session_state.user + '@' + st.session_state.server 
                print("DEBUG ", select )
                qsub_out = run("ssh -q " + creds  + \
                        ' qsub ' + select, 
                        capture_output=True, shell=True)   
                if qsub_out.returncode==0:                   
                    jobid = qsub_out.stdout.decode()
                    st.success('Qsub submitted to PBS, job id **[' + jobid + ']**')
                else:
                    st.write(qsub_out.stderr.decode())
                #print("DEBUG ", qsub_out.returncode )

            except:
                st.error( 'Qsub command not submitted')


        def get_cli_cmds():
            x,cmd = read_form()
            return cmd

        def get_qsub_cmds():
            cmd, x = read_form()
            return cmd

        def show_preview():
            cmd = get_qsub_cmds()
            s=''
            for k in cmd.keys():
                s += cmd[k] + '\n'                
            st.code(s)


        def show_cli_preview():
            cmd = get_cli_cmds()
            s='qsub '
            cmd['command'] = " -- " + cmd['command'] 
            for k in cmd.keys():
                s+= ' ' + cmd[k]
            st.code(s)


        ############################################################################################
        with pbs_tab: 
            if not inet.up():
                st.warning("No network connection")            
            with st.expander('PBS Job Parameters'):                    
                    setup_rp()
                    with st.form(key='pbs_form'):
                            setup_form()
                            #User_RPs = get_rp_list()                    
                            left1, centre1, centre2, right1 = st.columns(4)                    
                            with left1:
                                preview = st.form_submit_button('Preview PBS script')

                            with centre1:
                                preview_cli = st.form_submit_button('Preview qsub')


                            with centre2:
                                if inet.up():
                                    if st.session_state.modules == "" and st.session_state.command != "":
                                        subm_cli  = st.form_submit_button('Submit qsub command')
                                        if subm_cli:                                    
                                            if DRMAA_avail:
                                                submit_cli_qsub()
                                            else:
                                                submit_cli_qsub_ssh()

                                    with right1:
                                        if DRMAA_avail:
                                            subm_drmaa  = st.form_submit_button('Submit DRMAA')
                                        else:
                                            subm_ssh  = st.form_submit_button('Submit script',)

                            if preview: 
                                show_preview()
                            if preview_cli:  
                                show_cli_preview()
                            if 'programme' not in st.session_state.keys():
                                st.error("The allocated CHPC Research Programme code is required to submit jobs")
                            if not st.session_state.email:
                                st.warning("No email address given, notification mail directive omitted")


                    ############################  End form 

                    cmd_d=get_qsub_cmds()
                    text='\n'.join([cmd_d[k] for k in cmd_d.keys() ])
                    download = st.download_button('Download PBS script to local disk ' +\
                            st.session_state.dl_filename, text, 
                            file_name=st.session_state.dl_filename)
                               
                    if download:
                        st.info('Saving file ' +  st.session_state.dl_filename)                    
                                    
                    if st.session_state.user == "user":
                        st.error("Please give a valid username instead of " + st.session_state.user)
                    else:
                        if 'qsub_OK' in st.session_state.keys():
                                if st.session_state['qsub_OK']:
                                        if subm_ssh:
                                            send_pbs_file(st.session_state.dl_filename)
                                            submit_pbs_file(st.session_state.dl_filename)
                                            print("DEBUG after submit ssh")
                                            os.remove('/tmp/' + st.session_state.dl_filename)
                                else:
                                    st.error("Qsub from PBSwif not enabled")

                        if 'subm_drmaa' in st.session_state.keys():
                            if st.session_state['subm_drmaa']:
                                copy_pbs_file(st.session_state.dl_filename)
                                submit_pbs_file(st.session_state.dl_filename)
                            os.remove('/tmp/' + st.session_state.dl_filename)



            show_info()

