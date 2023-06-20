#pbs.py
import streamlit as st
from subprocess import run
import os,socket

saved_jobids=[]

try:
    import drmaa
    DRMAA_avail = True
except:
    DRMAA_avail = False


PBS_HOSTS = ['login1', 'login2', 'globus.chpc.ac.za']
host = socket.gethostname()

if host in PBS_HOSTS:
    CLUSTER_AVAIL=True
else:
    CLUSTER_AVAIL=False

import datetime
from common import check_select, DEFAULT_WALLTIME 
#ssh_clicked=False

def show_pbs(st, pbs_tab):
    
    pbs_text=''

#    def save_ssh_clicked():   
#        ssh_clicked=True

    def set_dl_filename():
        return st.session_state.dl_filename


    with pbs_tab:

        if not DRMAA_avail and not st.session_state.use_ssh:
            st.warning('PBS Job submission needs to run on a login node or SSH, neither available')

        with st.expander('PBS Job Parameters'):

                leftcol1, rightcol1 = st.columns([1,1])

                with leftcol1:
                    if st.session_state.user != "user":                 
                        ssh_button = st.button("Submit via ssh as " + st.session_state.user,
                                            key='ssh_button') #, on_click=save_ssh_clicked())
                    else:
                        st.error('Invalid SSH username \"' + st.session_state.user + '\"')
                        ssh_button = st.button('Please give a valid SSH username, not \"' \
                                           + st.session_state.user + '\"',
                                            key='ssh_button', disabled=True)

                with st.form(key='pbs_form'):
                                                        
                        form_leftcol, form_rightcol = st.columns([1,2])

                        with form_leftcol:
                    
                            jobname = st.text_input("PBS job name", value='MyJobName', 
                                                    key="jobname", max_chars=15,)

                            programme = st.text_input("**:red[CHPC Research Programme Code :warning:]**", 
                                                    placeholder='ABCD1234', key='programme', max_chars=8,
                                                    help='Provide your allocated RP code')
                        
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

                        if st.form_submit_button('Preview PBS script', use_container_width=True, type="primary"):
                            if not st.session_state.programme:
                                st.error("The allocated CHPC Research Programme code, e.g. 'ABCD1234' is required to submit jobs")
                            if not st.session_state.email:
                                st.warning("No email address given, notification mail directive omitted")

                            select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)

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
                            submission  = st.form_submit_button('Submit job script via DRMAA')
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
                            if st.session_state.use_ssh: #and st.session_state.ssh_button:

                                if st.session_state.user == "user":
                                    st.error("Invalid cluster username \"{}\"".format(st.session_state.user))
                                    return 
                                if not st.session_state.programme:
                                    st.error('No RP Code given')
                                    return 
                                else:
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
                                      
                                      #with st.spinner("Submitting job"):
                                        #try:
                                            CMD = 'scp ' + filename + ' ' + creds + ':' + st.session_state.workdir                                        
                                            print("DEBUG before ssh scp copy")
                                            exitcode = run(CMD,capture_output=True, shell=True) #, timeout=15.0, check=True)
                                            print("DEBUG after ssh scp copy " + exitcode.returncode)

                                        #except:# subprocess.TimeoutExpired as e:
                                            if exitcode.returncode < 0:
                                                st.error("Could not copy file to server, timeout " + filename + exitcode.returncode)
                                            #os.remove(filename)
                                                return
                                        
                                            st.info('File ' + filename + ' copied to cluster ' + \
                                                st.session_state.workdir + '/' + st.session_state.dl_filename)
#                                        #try:
                                            print("DEBUG before ssh qsub run")

                                            qsub_out = run("ssh " + creds  + \
                                                        ' qsub ' + st.session_state.workdir \
                                                        + '/' + st.session_state.dl_filename, 
                                                        capture_output=True, shell=True) #, timeout=15.0, check=True)                                            
                                        #except:# subprocess.TimeoutExpired as e:
                                            if qsub_out.returncode < 0:
                                                st.error("Timeout, Could not run qsub " + qsub_out.returncode)
                            
                                            if qsub_out.returncode == 0:
                                                jobid = qsub_out.stdout.decode()
                                                print("DEBUG after qsub " + jobid)

                                            #st.info("Job ID: " + jobid )

                                            os.remove(filename)
                                            print("DEBUG delete local pbs file")
                                    
                                        #st.success("Job ID: " + jobid )

                ##with botrightcol:

                st.download_button('Download PBS script to local disk' + st.session_state.dl_filename, 
                                   pbs_text,
                                   file_name=st.session_state.dl_filename, 
                                   use_container_width=True )
                    


                                
                
