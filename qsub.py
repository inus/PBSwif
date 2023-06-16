try:
  import drmaa
except:
    print("DRMAA not found")
    DRMAA_avail = False


from common import Setup_form, print_script

def show_qsub(st, qsub_tab):

  st.header='PBS Qsub'

  with qsub_tab:

    if not DRMAA_avail:
        st.warning('PBS job submission unavailable on this host', icon="⚠️")

    with st.form(key='qsub_form'):
      programme, email, select, command, queue, mails_on, jobname, workdir, modules = 'SCHPC', 'inus@chpc.ac.za',\
                 '-l select=1:ncpus=1', 'echo $(hostname) "Testing123"', 'serial', 'e', 'PBS-Jobname', '/home/$USER/lustre', \
                 "module add chpc/BIOMODULES python\nmodule add blast"
      Setup_form(st, programme, email, select, command, queue, mails_on, jobname, workdir, modules)

      configuration = st.form_submit_button('Preview PBS job script', use_container_width=True)

      if configuration:
        print_script(st, programme, email, select, command, queue, mails_on, jobname, st.session_state.Notify, modules) 

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
                  #print("Error in submitting job")
                  st.error( 'Your job has not been submitted')
      else:
          st.warning('PBS submission unavailable on this host')
          #nosubmission  = st.form_submit_button('PBS submission unavailable on this host', use_container_width=True)


