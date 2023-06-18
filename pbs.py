#pbs.py

try:
  import drmaa
  DRMAA_avail = True
except:
    DRMAA_avail = False

import datetime
from common import check_select, DEFAULT_WALLTIME 

def show_pbs(st, pbs_tab):

    def set_dl_filename():
        return st.session_state.dl_filename


    with pbs_tab:            

        with st.expander('PBS parameters'):

                form_leftcol, form_rightcol = st.columns([1,2])
            
                with st.form(key='pbs_form'):
                                                        
                        clear_on_submit = False

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
                            workdir = st.text_input("Working directory", key='workdir', 
                                                    help="Fill in to change directory to this")                     
                            modules = st.text_area("Modules and initialization code", 
                                                value="module load chpc/BIOMODULES python",
                                                key='modules', help="Any other initialization")
                        command = st.text_input("Commandline", 
                                                value="echo Hello from $(hostname) on $(date)", 
                                                key='command', help='Commands, switches and arguments')


                        if st.form_submit_button('Preview PBS script', use_container_width=True, type="primary"):
                            if not st.session_state.programme:
                                st.error("The allocated CHPC Research Programme code, e.g. 'ABCD1234' is required to submit jobs")
                            if not st.session_state.email:
                                st.warning("No email address given, notification mail directive omitted")
                            select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)
                            if st.session_state.bash:
                                st.text("#!/bin/bash")
                            st.text("#PBS -P " + programme)
                            if email and st.session_state.Notify:
                                st.text("#PBS -M " + email)
                                st.text("#PBS -m " + ''.join(mails_on))
                            st.text("#PBS " + select)
                            st.text("#PBS -q " + Queue)
                            if st.session_state.Vars: st.text("#PBS -V")
                            if st.session_state.jobname: st.text("#PBS -N " + st.session_state.jobname)
                            if st.session_state.Xfwd: st.text("#PBS -X")            
                            if st.session_state.Interactive:
                                st.text("#PBS -I")
                                st.info('You can start an interactive jobs as below')
                                cmd = 'qsub '
                                if st.session_state.Interactive: cmd = cmd + '-I '
                                if st.session_state.Vars: cmd = cmd + '-V '
                                if st.session_state.Xfwd: cmd = cmd + '-X '
                                cmd = cmd + '-N ' + st.session_state.jobname 
                                cmd = cmd + '-q ' + Queue 
                                cmd = cmd + ' ' + select
                                st.text(cmd)
                            else:
                                if st.session_state.join:
                                    st.text('#PBS -j oe')
                                if st.session_state.workdir:
                                    st.text('cd ' + st.session_state.workdir)
                                st.text(modules)
                                st.text(command)

                        if st.session_state.bash:
                            txt = ("#!/bin/bash\n")
                        else:
                            txt = ('## CHPC PBSwif generated script\n')

                        txt = txt + '## Script generated on ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'

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
                            if st.session_state.Vars: txt = txt + '#PBS -V ' + '\n'
                            if st.session_state.Xfwd: txt = txt + '#PBS -X ' + '\n'
                            txt = txt + '#PBS -N ' + st.session_state.jobname + '\n'
                            txt = txt + '#PBS -q ' + st.session_state.Queue + '\n'
                            txt = '#PBS ' + select + '\n'
                        else:
                            if st.session_state.workdir:
                                txt = txt + 'cd ' + st.session_state.workdir + '\n'
                            if st.session_state.join:
                                txt = txt + '#PBS -j oe' + '\n'

                            txt = txt + modules + '\n'
                            txt = txt + command + '\n'

                            dl_filename = st.text_input("Script file name", key='dl_filename',
                                                label_visibility='collapsed', 
                                                value=st.session_state.jobname + '.pbs.txt')


                        if DRMAA_avail:
                            submission  = st.form_submit_button('Submit PBS job script to Lengau Cluster', use_container_width=True)
                            if submission:
                                pbs = drmaa.Session()
                                try:
                                    pbs.initialize()
                                except:
                                    pass

                                jt = pbs.createJobTemplate()
                                jt.remoteCommand = command
                                jt.jobName = jobname
                                jt.workingDirectory = workdir
                                jt.nativeSpecification = select + " -P " + programme 
                                jt.email = email 

                                try:
                                    jobid = pbs.runJob(jt)
                                    st.success('Your job has been submitted with id ' + jobid )
                                except:
                                    st.error( 'Your job could not be submitted. Check if your RP code is valid')
                        else:
                            st.warning('PBS submission unavailable on this host')


                st.download_button('Download PBS script', data=txt, file_name=st.session_state.dl_filename, on_click=set_dl_filename, use_container_width=True )
