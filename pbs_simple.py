

from common import Setup_form, configuration

def show_simple_pbs(st,simple_pbs_tab):


  with simple_pbs_tab:
  
    Notify  = st.checkbox("Receive job emails", key = "Notify")
    with st.form(key='simple_pbs_form'):
      project, email, select, command, queue, mails_on, jobname, workdir, modules  = \
            'RCHPC', 'email@address', '-l select=1:ncpus=3', \
            'echo $(hostname) "Testing123"', 'serial', 'e', 'TestPBSjob', '$USER/lustre', "module load chpc/BIOMODULES python\nmodule add blast"
      Setup_form(st, project, email, select, command, queue, mails_on, jobname, workdir, modules)
      configuration = st.form_submit_button('Write PBS script', use_container_width=True, type="primary")

    if configuration:
        st.text("#PBS -P " + project)
        if email and Notify:
            st.text("#PBS -M " + email)
            st.text("#PBS -m " +  ''.join(mails_on))
        st.text("#PBS " + select)
        st.text("PBS -q " + queue)
        st.text(modules)
        st.text(command)

