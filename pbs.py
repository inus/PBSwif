#pbs.py

try:
  import drmaa
except:
    DRMAA_avail = False

import datetime
from common import check_select, DEFAULT_WALLTIME 

def show_pbs(st, pbs_tab):

    def set_dl_filename():
        #print("onclick!", 'PBShelper.pbs')
        return st.session_state.dl_filename
        
    with pbs_tab:            

        form_leftcol, form_rightcol = st.columns([1,2])
      
        with st.form(key='pbs_form'):
                                                
                clear_on_submit = False
                with form_leftcol:
            
                    jobname = st.text_input("PBS job name", value='MyJobName', key="jobname")

                    programme = st.text_input("**:red[CHPC Research Programme Code *]**", placeholder='ABCD1234', key='programme')
                
                    mails_on  = st.multiselect("Send emails on job begin/end/abort events",  ['b', 'e', 'a'],
                                                default = 'e', key='mails_on', disabled = not st.session_state.Notify )
                
                    email = st.text_input("Email address", placeholder='your@email.addr', key='email')
                
                    timecol1, timecol2 = st.columns([1,1])
                    with timecol1:
                        walltime = st.number_input('Walltime h', value=DEFAULT_WALLTIME, key='walltime' )
                    with timecol2:
                        walltime_m = st.number_input('Walltime min', value=0, key='walltime_m' )


                with form_rightcol:
                    errorfile = st.text_input("Error file name - leave empty to use jobname.job-id", key='error')
                    outfile = st.text_input("Output file name - leave empty to use jobname.job-id", key='out'  )
                    workdir = st.text_input("Working directory", key='work')
                     
                    modules = st.text_area("Modules and other initialization code", value="module load chpc/BIOMODULES python",
                                           key='modules')
                    command = st.text_input("Command to run", value="echo Hello from $(hostname) on $(date)", key='command')


                if st.form_submit_button('Preview PBS script', use_container_width=True, type="primary"):
                    if not st.session_state.programme:
                        st.error("The allocated CHPC Research Programme code, e.g. 'ABCD1234' is required to submit jobs")
                    if not st.session_state.email:
                        st.warning("No email address given, notification mail directive omitted")
                    select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)
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
                        st.text(modules)
                        st.text(command)
            
                txt = "#PBS -P " + programme + '\n'

                if email and st.session_state.Notify:
                        txt = txt + "#PBS -M " + email + '\n'
                        txt = txt + "#PBS -m " + ''.join(mails_on) + '\n'
                select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs = check_select(st)
                txt = txt + select + '\n'
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
                    txt = txt + modules + '\n'
                    txt = txt + command + '\n'

        dl_file_col_left, dl_file_col_right = st.columns([1,1])
        with dl_file_col_left:
            dl_filename = st.text_input("Script file name", key='dl_filename',
                                         label_visibility='collapsed', 
                                         value=st.session_state.jobname + '.pbs.txt')
        with dl_file_col_right:
            st.download_button('Download PBS script', data=txt, 
                                file_name=st.session_state.dl_filename,
                                on_click=set_dl_filename,
                                use_container_width=True )


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
                    st.error( 'Your job could not be submitted')
        else:
            st.warning('PBS submission unavailable on this host')


