#pbs.py

try:
  import drmaa
except:
    print("DRMAA not found")
    DRMAA_avail = False

import datetime
from common import check_select

def show_pbs(st, pbs_tab):

    with pbs_tab:            

        col1, col2 = st.columns([1,2])
      
        with st.form(key='pbs_form'):
                                                
                clear_on_submit = False
                with col1:
            
                    jobname = st.text_input("PBS job name", value='MyJobName', key="jobname")

                    programme = st.text_input("CHPC Research Programme", placeholder='CHPC1234', key='programme')
                
                    mails_on  = st.multiselect("Notify emails on begin/end/abort ",  ['b', 'e', 'a'],
                                                default = 'e', key='mails_on', disabled= not st.session_state.Notify )
                
                    email = st.text_input("Email address", placeholder='your@email.addr', key='email')
                
                    walltime = st.number_input('Walltime h', value=48, key='walltime' )


                with col2:
                    errorfile = st.text_input("Error file name - leave empty to use jobname.job-id", key='error')
                    outfile = st.text_input("Output file name - leave empty to use jobname.job-id", key='out'  )
                    workdir = st.text_input("Working directory", key='work')
                     
                    modules = st.text_area("Modules and other initialization code", value="module load chpc/BIOMODULES python",
                                           key='modules')
                    command = st.text_input("Command to run", value="echo Hello from $(hostname) on $(date)", key='command')


                if st.form_submit_button('Preview PBS script', use_container_width=True, type="primary"):
                    if not st.session_state.programme:
                         st.error("CHPC programme Code needed")
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

        st.download_button('Download PBS script', file_name='pbs-helper.pbs', data = txt)

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


