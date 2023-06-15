import drmaa
from common import Setup_form, configuration, print_script

def show_qsub(st, qsub_tab):

  with qsub_tab:
    Notify = st.checkbox("Receive job emails", key = "qsubNotify")
    with st.form(key='qsub_form'):
      programme, email, select, command, queue, mails_on, jobname, workdir = 'SCHPC', 'inus@chpc.ac.za',\
                 '-l select=1:ncpus=1', 'echo $(hostname) "Testing123"', 'serial', 'e', 'PBS-Jobname', '/home/$USER/lustre'
      Setup_form(st, programme, email, select, command, queue, mails_on, jobname, workdir)

      configuration = st.form_submit_button('Preview PBS job script', use_container_width=True)

      submission  = st.form_submit_button('Submit PBS job script to Lengau Cluster', use_container_width=True)

      if configuration:
        print_script(st, programme, email, select, command, queue, mails_on, jobname, Notify) 

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
            #print("Error in submitting job")
            st.error( 'Your job has not been submitted')



