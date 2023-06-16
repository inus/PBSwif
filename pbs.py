#pbs.py
import datetime
from common import print_script


def show_pbs(st, pbs_tab):

    def check_select(): 

        Nodes, Cores, Memory, Queue, MPIprocs, GPUs = st.session_state.Nodes, st.session_state.Cores, \
                    st.session_state.Memory, st.session_state.Queue, st.session_state.MPIprocs, st.session_state.GPUs

        if Nodes == 1 and Memory < 120:
            Queue = 'serial'
            if Cores >= 23:
                Cores = st.session_state.Cores
            if MPIprocs:
                MPIprocs = Cores
        elif Nodes > 1:
            Cores = 24
            if MPIprocs:
                MPIprocs = Cores
            Queue = 'normal'
        elif Nodes > 20:
            Queue = 'large'
        else:
            Queue = 'normal'

        if Memory > 120 or Cores > 24 :
            Queue = 'bigmem'
    
        if MPIprocs > Cores:
            MPIprocs = Cores
    
        if MPIprocs != 0:
            select = "#PBS -l select={}:ncpus={}:mpiprocs={}:mem={}GB".format(Nodes,Cores,MPIprocs,Memory)
        else:
            select = "#PBS -l select={}:ncpus={}:mem={}GB".format(Nodes,Cores,Memory)

        if GPUs != 0:
            select = "#PBS -l select={}:ncpus={}:ngpus={}:mpiprocs={}:mem={}GB".format(Nodes,Cores,GPUs,MPIprocs,Memory)
            Queue = 'gpu_' + str(st.session_state.GPUs)
        

        if st.session_state.Place and st.session_state.PlaceSelect:
            select = select + " -l place={}".format(st.session_state.PlaceSelect)

        if st.session_state.walltime:
            select = select + " -l walltime=" + str(st.session_state.walltime) + ':00'
        
        return select


    with pbs_tab:            

        col1, col2 = st.columns([1,2])
      
        with st.form(key='pbs_form'):
                
                clear_on_submit = False
                with col1:
            
                    jobname = st.text_input("PBS job name", value='MyJobName', key="jobname")

                    programme = st.text_input("CHPC Research Programme", placeholder='CHPC1234')
                
                    mails_on  = st.multiselect("Notify emails on begin/end/abort ",  ['b', 'e', 'a'], default = 'e')
                
                    email = st.text_input("Email address", value='your@email.addr')
                
                    walltime = st.number_input('Walltime h', value=48, key='walltime', )


                with col2:
                     
                    modules = st.text_area("Modules and other initialization code", value="module load chpc/BIOMODULES python")
                    command = st.text_input("Command to run", value="echo Hello from $(hostname) on $(date)")


                if st.form_submit_button('Write PBS script to screen', use_container_width=True, type="primary"):
                    select = check_select()
                    st.text("#PBS -P " + programme)
                    if email and st.session_state.Notify:
                        st.text("#PBS -M " + email)
                        st.text("#PBS -m " + ''.join(mails_on))
                    st.text(select)
                    st.text("#PBS -q " + st.session_state.Queue)
                    if st.session_state.Vars:
                        st.text("#PBS -V")
                    if st.session_state.jobname:
                        st.text("#PBS -N " + st.session_state.jobname )
            
                    if st.session_state.Interactive:
                        st.text("#PBS -I")
                        st.info('You can start an interactive jobs as below')
                        cmd = 'qsub '
                        if st.session_state.Interactive: cmd = cmd + '-I '
                        if st.session_state.Vars: cmd = cmd + '-V '
                        if st.session_state.Xfwd: cmd = cmd + '-X '
                        cmd = cmd + '-N ' + st.session_state.jobname 
                        cmd = cmd + '-q ' + st.session_state.Queue 
                        cmd = cmd + ' ' + select
                        st.text(cmd)
                    else:
                        st.text(modules)
                        st.text(command)
            
                txt = "#PBS -P " + programme + '\n'

                if email and st.session_state.Notify:
                        txt = txt + "#PBS -M " + email + '\n'
                        txt = txt + "#PBS -m " + ''.join(mails_on) + '\n'
                select = check_select()
                txt = txt + select + '\n'
                txt = txt + "#PBS -q " + st.session_state.Queue + '\n'
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
                    #txt = txt + cmd
                else:
                    txt = txt + modules + '\n'
                    txt = txt + command + '\n'

        st.download_button('Download PBS script', file_name='pbs-helper.pbs', data = txt)

