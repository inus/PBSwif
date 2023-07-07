#pbs.py
try:
    import drmaa
    DRMAA_avail = True
except:
    DRMAA_avail = False

import datetime
import streamlit as st
from subprocess import run, TimeoutExpired
import os,socket
import inet

from common import show_info, check_select
from sidebar import DEFAULT_WALLTIME 
from shell import run_cluster_cmd


PBS_HOSTS = ['login1', 'login2', 'globus.chpc.ac.za']
host = socket.gethostname()

if host in PBS_HOSTS:
    PBS_HOST=True
else:
    PBS_HOST=False

User_RPs = []


def show_pbs(st, pbs_tab):

        Resource_List = ['nodect', 'ncpus', 'mpiprocs', 'ngpus',
                         'mem', 'place', 'walltime']
        PBS_dict = {
            'bash': '#!/bin/bash', 'programme': 'P', 
            'email': 'M', 'jobname': 'N', 'Queue': 'q',  
            'error': 'e', 'out': 'o', 'join': 'j oe',  
            'Interactive' : 'I', 'Xfwd': 'X', 'Vars': 'V',  
            'Select'      : Resource_List,}
        
        dl_file_contents=''


# Resource_List: []
#{'mem': '120gb', 'mpiprocs': 4,
#  'ncpus': 4, 'nodect': 1, 'place': 'free', 'select': '1:ncpus=4:mpiprocs=4:mem=120GB',
#  'walltime': '01:00:00'}

#['mem', 'mpiprocs','ncpus','nodect', 'place','select', 'ngpus']
#  'walltime': '01:00:00'}

#         select = "-l select={}:ncpus={}:ngpus={}:mpiprocs={}:mem={}GB".format(Nodes,Cores,GPUs,MPIprocs,Memory)


        @st.cache_data(persist="disk")
        def get_rp_detail(pgms):
            prm = '|'.join(pgms)

            op=run_cluster_cmd(st.session_state.user + '@' + st.session_state.server,
                {'vrp': "cat /home/userdb/projects_status.csv | grep -E \'" + prm + "\'" },'vrp','')        

            if op is not None:
                lines = op.splitlines()
                
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

            op=run_cluster_cmd(st.session_state.user + '@' + st.session_state.server,
                {'rp': 'grep ischeepers /home/userdb/programme_info.csv'},'rp','') # fake cmd dict
            
            pgms = []
            opl = op.splitlines()
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
                    #
                    #if 'user_rp' in st.session_state.keys():
                    #    st.session_state.user_rp.help = 'Select RP code for details'


        ############################################################################################
        with pbs_tab: 

            if not inet.up():
                st.warning("No network connection")            

            with st.expander('PBS Job Parameters'):

                    leftcol1, centrecol1, rightcol1 = st.columns([1,1,1])

                    with leftcol1:
                        if not DRMAA_avail:
                                if st.session_state.user != "":                 
                                    ssh_button = st.button("Submit via ssh as " + 
                                                        st.session_state.user + '@' +
                                                        st.session_state.server, 
                                                key='ssh_button', 
                                                disabled=(st.session_state.user == "" or \
                                                           not inet.up() or not st.session_state.qsub_ok) )
                                else:
                                    st.warning("No ssh username")
                                    st.error('Invalid SSH username \"' + st.session_state.user + '\"')
                                    ssh_button = st.button('Please give a valid SSH username, not \"' \
                                            + st.session_state.user + '\"',
                                                key='ssh_button', disabled=True)

                    with centrecol1:
                        rp_info_place = st.empty() 
                        if st.checkbox("Get RP", key='getrp', help='(Re)Select RP code for programme info'):
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
                                                rp_dict, rp_info_place)) 
                                #show_rp_info(rp_dict, rp_info_place)
                            else:
                                RP_selectbox_labels = ''
                                st.selectbox("CHPC Research Programme Code", 
                                             RP_selectbox_labels, key='user_rp',
                                             on_change=show_rp_info(
                                                rp_dict, rp_info_place)) 
                                
    
                    ###########################################################
                    with st.form(key='pbs_form'):
                                                            
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
                                    with lcol1:
                                        mail_on_b = st.checkbox('b', key='mail_on_begin', help='Begin')
                                    with ccol1:
                                        mail_on_e = st.checkbox('e', key='mail_on_end', help='End', value=True)
                                    with rcol1:
                                        mail_on_a = st.checkbox('a', key='mail_on_abort', help='Abort')

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

############################                    ############################### end of form

                            if st.form_submit_button('Preview PBS script'):
                                if 'programme' not in st.session_state.keys():
                                    st.error("The allocated CHPC Research Programme code is required to submit jobs")
                                if not st.session_state.email:
                                    st.warning("No email address given, notification mail directive omitted")

                                select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)


                                Resource_dict = {}
                                for k in Resource_List:
                                    Resource_dict[k] = st.session_state[k]

                                cmd = {}; qs_cmd={}; sel = {}
                                for k in PBS_dict:
                                    if k=='Select':
                                        for j in Resource_List: 
                                                if st.session_state[j]:
                                                    sel[j] = st.session_state[j] 
                                        break
                                    else:
                                        if k in st.session_state.keys():
                                            if k=='bash':
                                                if st.session_state[k]:
                                                    cmd[k] = PBS_dict[k]
                                            elif k in ['jobname', 'email', 'Queue', 'programme']:
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
                                                    qs_cmd[k] =   '-' + PBS_dict[st.session_state[k]] + ' ' + st.session_state[k] 
                                                    cmd[k] = '#PBS ' + qs_cmd[k]



                                selstr =  '-l select={}:ncpus={}:mpiprocs={}:mem={}GB -l walltime={} '.format(
                                        sel['nodect'], sel['ncpus'], sel['mpiprocs'], sel['mem'], 
                                        #sel['ngpus'],
                                        sel['walltime'],)
                                
                                qs_cmd['Select'] = selstr
                                cmd['Select']  = '#PBS ' + selstr
                                cmd['modules'] = st.session_state.modules
                                cmd['command'] = st.session_state.command

                                for k in cmd.keys():
                                    st.text(cmd[k]) 
                                    dl_file_contents += cmd[k] + '\n'

                                fp = open('/tmp/' + st.session_state.jobname + '.pbs', 'w')
                                fp.write(dl_file_contents); fp.close()


#{'nodect': 1}{'mem': 120}{'ncpus': 4}{'mpiprocs': 16}{'cputype': 'haswell'}{'walltime': '48:00:00'}
#testfat.pbs:#PBS -l select=1:ncpus=56:mpiprocs=56:mem=1000GB -l walltime=24:00:00 -l place=excl


                            if DRMAA_avail:
                                if inet.up():
                                    submission  = st.form_submit_button('Submit job script via DRMAA')
                                else:
                                    submission  = st.form_submit_button('Submit job script via DRMAA',
                                                                        disabled=True)
                                if submission:
                                    pbs = drmaa.Session()
                                    try:
                                        pbs.initialize()
                                    except:
                                        pass

                                    select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)

                                    jt = pbs.createJobTemplate()
                                    jt.remoteCommand = st.session_state.command
                                    jt.jobName = jobname
                                    jt.workingDirectory = workdir

                                    jt.nativeSpecification = select + " -P " + programme 
                                    jt.email = email 

                                    try:
                                        jobid = pbs.runJob(jt)
                                        st.success('Job has been submitted to PBS, job id **[' + jobid + ']**')
                                    except:
                                        st.error( 'PBS job not submitted. Check if your RP programme code is valid')
                            else: #ssh 

                                #if st.session_state.use_ssh: 

                                    if st.session_state.user == "user":
                                        st.error("Invalid cluster username \"{}\"".format(st.session_state.user))
                                        return 

                                    #if not st.session_state.programme and not st.session_state.getrp:
                                    if not st.session_state.getrp: 
                                        st.info("No RP info ")

                                    else:

                                        if not st.session_state.programme:
                                            st.warning('No RP Code given')
                                            programme='TBD'

                                        #return 
                    ############################  End form 

                    if 'dl_filename' in st.session_state.keys():
                        if len(dl_file_contents)==0:
                            print("Reading tmp jobfile")


                        if st.download_button('Download PBS script to local disk ' + st.session_state.dl_filename,
                                               dl_file_contents, file_name=st.session_state.dl_filename):
                            st.info('Downloading file ' +  st.session_state.dl_filename)
                    
                
                    creds = st.session_state.user + '@' + st.session_state.server 
                    
                    if st.session_state.user == "user":
                        st.error("Please give a valid username instead of " + st.session_state.user)
                    else:
                        if st.session_state.qsub_ok:
                                
                            if ssh_button:
                                
                                filename='/tmp/' + st.session_state.dl_filename 

#                                fp = open(filename, 'w'); fp.write(dl_file_contents); fp.close()
                                fp = open(filename, 'r')
                                dl_file_contents=fp.read(); fp.close()

                                st.warning("Copying job file via scp " + st.session_state.server)
                                CMD = 'scp ' + filename + ' ' + creds + ':' + st.session_state.workdir                                    
                                exitcode = run(CMD, capture_output=True, shell=True) 

                                if exitcode.returncode < 0:
                                    st.error("Could not copy file to server, timeout " + filename + exitcode.returncode)
                                    return
                            
                                st.info('File ' + filename + ' copied to cluster ' + \
                                    st.session_state.workdir + '/' + st.session_state.dl_filename)
                                
                                qsub_out = run("ssh " + creds  + \
                                            ' qsub ' + st.session_state.workdir \
                                            + '/' + st.session_state.dl_filename, 
                                            capture_output=True, shell=True)                                        
                                
                                if qsub_out.returncode < 0:
                                    st.error("Timeout, Could not run qsub " + qsub_out.returncode)
                                    print("ERROR: Timeout, qsub command failed to send")
                                    return
                                else:
                                    print("INFO: qsub command sent :", ' qsub ' + 
                                    st.session_state.workdir \
                                    + '/' + st.session_state.dl_filename)
                                    st.info('qsub command sent')


                                if qsub_out.returncode == 0:
                                    jobid = qsub_out.stdout.decode()
                                    st.success('Job ' + str(jobid) + 'submitted')
                                    print("INFO: post qsub ", qsub_out.stdout.decode())



                                #os.remove(filename)
                        else:
                                print("Qsub remote not active")
                                st.error("Qsub from PBSwif not enabled")




            show_info(st)

