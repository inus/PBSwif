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

from common import show_info, check_select, DEFAULT_WALLTIME 
from shell import run_cluster_cmd

User_RPs = []

PBS_HOSTS = ['login1', 'login2', 'globus.chpc.ac.za']
host = socket.gethostname()

if host in PBS_HOSTS:
    PBS_HOST=True
else:
    PBS_HOST=False


def show_pbs(st, pbs_tab):


        Resource_List = ['nodect', 'ncpus', 'mpiprocs', 'ngpus',
                     'mem', 'place','select', 'walltime']
        PBS_dict = {
            'programme' : 'P', 
            'email'     : 'm', 
            'email_abe' : 'a' ,  
            #'email_on_e' : 'e' ,  
            #'email_on_b' : 'b' ,  
        
            'jobname'  : 'N',
            'Queue'    : 'q',  

            #'walltime' : 'walltime', 
            #'Resource' : Resource, 

            #'cputype' : 'cputype', 
            #'Memory' : 'mem',
            #'Cores' : 'ncpus',
            #'nodes' : '',
            #'GPUs'   : 'ngpus',   
            #'MPIprocs' : 'mpiprocs', 
            'error'  : 'e', 
            'out'    : 'o', 
            'join'   : 'j oe',  
            'Interactive' : 'I',
            'Xfwd'  :        'X', 
            #'Nodes' : '',  << nodect 
            'Vars'  : 'V' }
#            'bash'   : '#!/bin/bash',


# Resource_List: []
#{'mem': '120gb', 'mpiprocs': 4,
#  'ncpus': 4, 'nodect': 1, 'place': 'free', 'select': '1:ncpus=4:mpiprocs=4:mem=120GB',
#  'walltime': '01:00:00'}

#['mem', 'mpiprocs','ncpus','nodect', 'place','select', 'ngpus']
#  'walltime': '01:00:00'}

#         select = "-l select={}:ncpus={}:ngpus={}:mpiprocs={}:mem={}GB".format(Nodes,Cores,GPUs,MPIprocs,Memory)


        pbs_text=''

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
                            pgm_dict[pgm] = {'start': line[1],
                                        'end': line[2],
                                        'alloc': line[3],
                                        'cpuh': line[4]
                                        }                             
#                st.session_state['rp_fetched'] = True
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
            #st.session_state['user_rp_fetched'] = True    # <<< ????
            return user_rps 
        
        
            
        def set_dl_filename():
            return st.session_state.dl_filename
        
        def show_rp_info(rp_dict, place):
                
                def show_rp_data():
                    with place.container():                    
#                        st.info(rp_dict[st.session_state.user_rp]['start'] + ' -- ' +
#                                rp_dict[st.session_state.user_rp]['end'])

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
                    print("DEBUG in show_rp_info:", ) #rp_dict.keys(), place)    
                    show_rp_data()

                else: # still no data?
                    print("DEBUG in show_rp_info: no key", ) #rp_dict.keys(), place)    
                    if 'user_rp' in st.session_state.keys():
                        show_rp_data() 



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
                        if st.checkbox("Get RP", key='getrp', ):
                            User_RPs = get_rp_list()                    

                    with rightcol1:

                        rp_info_place2 = st.empty() 

                        if st.session_state.getrp:

                            if not 'rp_dict' in locals() or 'rp_dict' in globals():
                                print("DEBUG NO RP DICT")
                                rp_dict = get_rp_list()

                            if rp_dict:
                                RP_selectbox_labels = rp_dict.keys() 
                                st.selectbox("CHPC Research Programme Code", 
                                             RP_selectbox_labels, key='user_rp',
                                             on_change=show_rp_info(
                                                rp_dict, rp_info_place)) 
                                show_rp_info(rp_dict, rp_info_place)                                                                        
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
                                                        value='MyJobName', 
                                                        key="jobname", max_chars=15,)


                                if st.session_state.getrp:
                                    if st.session_state.user_rp == "":
                                        msg = "**:red[CHPC Research Programme Code :warning:]**"
                                    else:
                                        msg = "CHPC Research Programme Code" 

                                    programme = st.text_input(msg, 
                                                        placeholder='CHPC9999', key='programme', max_chars=8,
                                                        help='Provide your CHPC allocated RP code',
                                                        value = st.session_state.user_rp)
                            
                                mails_on  = st.multiselect("Email on job events",
                                                            ['b', 'e', 'a'], default = 'e',
                                                            key='mails_on', 
                                                            help = "Send email on job events: **b**egin/**e**nd/**a**bort"  )
                            
                                email = st.text_input("Email address", placeholder='your@email.addr',
                                                    key='email', help="Fill in to receive email")
                                
                                col_left, col_right = st.columns([1,1])

                                with col_left:
                                    bash  = st.checkbox("Enable bash", key="bash", value=True,
                                                    help="Add bash to script to enable bash variables and constucts")
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

                            if st.form_submit_button('Preview PBS script'):
                                if 'programme' not in st.session_state.keys():
                                #if not st.session_state.programme:
                                    st.error("The allocated CHPC Research Programme code, e.g. 'ABCD1234' is required to submit jobs")
                                if not st.session_state.email:
                                    st.warning("No email address given, notification mail directive omitted")
#############################
                                select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)

                                pbs_text1 = ''
                                qsub_cmd1 = ''

                                Resource_dict = {}
                                for k in Resource_List:
                                    Resource_dict[k] = st.session_state[k]

                                cmd = {}; qs_cmd={}
                                for k in PBS_dict:
                                    if k=='Resource': break 
                                    cmd[k] = '#PBS ' + '-' + PBS_dict[k] + '\n'
                                    #pbs_text1 += '#PBS ' + '-' + PBS_dict[k] + '\n'
                                    #qsub_cmd1 += '-' +  PBS_dict[k] + ' '
                                    qs_cmd[k] = '-' +  PBS_dict[k] + ' '

                                print("DEBUG \n\n\n", pbs_text1, )
                                print("DEBUG ______________________________ \n\n\n", qsub_cmd1)


                                if st.session_state.bash:
                                    st.text("#!/bin/bash")
                                    pbs_text +=  "#!/bin/bash\n"
                                    qsub_cmd = 'qsub '

                                if programme:
                                    st.text("#PBS -P " + programme)
                                    pbs_text += "#PBS -P " + programme + '\n'
                                    qsub_cmd += ' -P ' + programme
                                else:
                                    st.text("#PBS -P " + 'RPCODE')
                                    pbs_text += "#PBS -P RPCODE\n"
                                    qsub_cmd += ' -P ' + 'RPCODE'

                                qsub_cmd += ' -N ' + st.session_state.jobname  + ' '
                                pbs_text += '#PBS -N' + st.session_state.jobname + '\n'

                                if email and st.session_state.Notify:
                                    st.text("#PBS -M " + email) 
                                    pbs_text += "#PBS -M " + email + '\n'
                                    st.text("#PBS -m " + ''.join(mails_on))
                                    pbs_text = "#PBS -m " + ''.join(mails_on) +'\n'
                                    
                                st.text("#PBS " + select)
                                pbs_text = "#PBS " + select + '\n'
                                qsub_cmd += select

                                st.text("#PBS -q " + Queue)
                                pbs_text = "#PBS -q " + Queue + '\n'
                                qsub_cmd += ' -q ' + Queue

                                ts = 'walltime=' + str(st.session_state.walltime ) + ':' + \
                                                str(st.session_state.walltime_m)
                                st.text("#PBS -l " + ts)
                                pbs_text += "#PBS -l " + ts + '\n'
                                qsub_cmd += ' -l ' + ts 


                                if st.session_state.Vars:
                                    st.text("#PBS -V")
                                    pbs_text += "#PBS -V\n"
                                    qsub_cmd +=  ' -V '

                                if st.session_state.jobname: 
                                    st.text("#PBS -N " + st.session_state.jobname)
                                    pbs_text += "#PBS -N " + st.session_state.jobname + '\n'

                                if st.session_state.Xfwd: 
                                    st.text("#PBS -X")
                                    pbs_text += "#PBS -X \n"
                                    qsub_cmd +=  ' -X '

                                if st.session_state.Interactive:
                                    st.text("#PBS -I")
                                    pbs_text += "#PBS -I\n"
                                    qsub_cmd += ' -I' 
                                    st.info('Start an interactive cluster job as below, use your own RPCODE')
                                    st.text(qsub_cmd, help="Copy and paste to a ssh session on a login node")
                                else: 
                                    # join error and output files if not interactive
                                    if st.session_state.join:
                                        st.text('#PBS -j oe')
                                        pbs_text += '#PBS -j oe\n'

                                if st.session_state.workdir:
                                        st.text('cd ' + st.session_state.workdir)
                                        pbs_text += 'cd ' + st.session_state.workdir + '\n'

                                    
                                st.text(modules)
                                pbs_text += st.session_state.modules + '\n'

                                st.text(command) 
                                pbs_text += st.session_state.command + '\n' 

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
                                    
                                        filename = '/tmp/' + st.session_state.dl_filename 
                                        fp = open( filename, 'w')
                                        if st.session_state.bash:
                                            txt = ("#!/bin/bash\n")
                                        else:
                                            txt = ('## PBSwif autogenerated script\n')
                                        txt = txt + '## PBS Script generated on ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'
                                        txt = txt + "#PBS -P " + programme + '\n'
                                        if email:
                                                txt = txt + "#PBS -M " + email + '\n'
                                                txt = txt + "#PBS -m " + ''.join(mails_on) + '\n'
                                        select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)
                                        txt = txt + "#PBS " + select + '\n'
                                        txt = txt + "#PBS -q " + Queue + '\n'
                                        if st.session_state.Vars:
                                            txt = txt + "#PBS -V" + '\n'
                                        if st.session_state.jobname:
                                            txt = txt + "#PBS -N " + st.session_state.jobname + '\n'

                                        if st.session_state.Interactive:
                                            txt = txt + "#PBS -I" + '\n'
                                            if st.session_state.Vars: 
                                                txt = txt + '#PBS -V ' + '\n'
                                            if st.session_state.Xfwd:
                                                txt = txt + '#PBS -X ' + '\n'
                                            txt = txt + '#PBS -N ' + st.session_state.jobname + '\n'
                                            txt = txt + '#PBS -q ' + st.session_state.Queue + '\n'
                                            txt = '#PBS ' + select + '\n'
                                        else:
                                            if st.session_state.workdir:
                                                txt = txt + 'cd ' + st.session_state.workdir + '\n'
                                            if st.session_state.join:
                                                txt = txt + '#PBS -j oe' + '\n'


                                        txt = txt + "## Modules\n"
                                        txt = txt + st.session_state.modules + '\n'
                                        txt = txt + "## Command \n"
                                        txt = txt + st.session_state.command + '\n'
                                        txt = txt + "## End\n"
                                        pbs_text += txt

                                        fp.write(txt)
                                        fp.close()


                                        creds = st.session_state.user + '@' + st.session_state.server 
                                        
                                        if st.session_state.user == "user":
                                            st.error("Please give a valid username instead of " + st.session_state.user)
                                        else:
                                            if st.session_state.qsub_ok:
                                                    
                                                if ssh_button:
                                                    

                                                    st.warning("Submitting job via ssh " + st.session_state.server)
                                                    CMD = 'scp ' + filename + ' ' + creds + ':' + st.session_state.workdir                                        
                                                    exitcode = run(CMD,capture_output=True, shell=True) #, timeout=15.0, check=True)
                                                    print("INFO: SCP command sent :", filename)

                                                    if exitcode.returncode < 0:
                                                        st.error("Could not copy file to server, timeout " + filename + exitcode.returncode)
                                                        return
                                                
                                                    st.info('File ' + filename + ' copied to cluster ' + \
                                                        st.session_state.workdir + '/' + st.session_state.dl_filename)

                                                    print("INFO: SCP command sent :", 
                                                                'scp ' + filename + ' ' + creds + ':' +
                                                                st.session_state.workdir)
                                                    
                                                    qsub_out = run("ssh " + creds  + \
                                                                ' qsub ' + st.session_state.workdir \
                                                                + '/' + st.session_state.dl_filename, 
                                                                capture_output=True, shell=True) #, timeout=15.0, check=True)                                            
                                                    
                                                    if qsub_out.returncode < 0:
                                                        st.error("Timeout, Could not run qsub " + qsub_out.returncode)
                                                        print("ERROR: Timeout, QSUB command not sent :")

                                                    print("INFO: QSUB command sent :", ' qsub ' + 
                                                        st.session_state.workdir \
                                                        + '/' + st.session_state.dl_filename)


                                                    if qsub_out.returncode == 0:
                                                        jobid = qsub_out.stdout.decode()
                                                        st.success('Job ' + str(jobid) + 'submitted')


                                                    os.remove(filename)
                                            else:
                                                    print("Qsub remote not active")
                                                    st.error("Qsub from PBSwif not enabled")

                    st.download_button('Download PBS script to local disk' + st.session_state.dl_filename, 
                                    pbs_text,
                                    file_name=st.session_state.dl_filename, 
                                    use_container_width=True )



            show_info(st)

