
from common import show_email_options, configuration

def show_pbs(st, pbs_tab):

    with pbs_tab:
      
      Notify  = st.checkbox("Receive job emails", key='notify2', on_change=show_email_options(st))

      with st.form(key='pbs_form'):
        clear_on_submit = False
        Nodes = st.number_input("Number of nodes",value=1)
        Cores = st.selectbox("Cores", [1,2,3,4,5,6,7,8,9,10,11,12,
                                       13,14,15,16,17,18,19,20,21,22,23,24,25,28,56], index=23)
        MPIprocs = st.selectbox("MPI Cores", [0,1,2,3,4,5,6,7,8,9,10,11,12,
                                       13,14,15,16,17,18,19,20,21,22,23,24,25,28,56], index=24)
    
        Memory = st.selectbox("Memory in GB",  [60,120,500,1000], index=1)
        Queue = st.selectbox("Queue",  ['serial','seriallong', 'smp','normal', 'large','xlarge','bigmem',
    'vis','test','gpu_1','gpu_2','gpu_3','gpu_4','gpu_long','express'], index=3)
    
    #    CPUtype = st.selectbox("CPU type", ['haswell','haswell_fat',])
        Interactive  = st.checkbox("Run interactive commands on node", key="Interactive")
        Vars  = st.checkbox("Preserve current shell variables", key="Vars")
    
        programme = st.text_input("CHPC Research Programme code", value='RP-CODE')
    
        Place  = st.checkbox("Select job placement")
        PlaceSelect = st.selectbox("Placement", ["free", "excl"])
    
        mails_on  = st.multiselect("Notify emails on begin/end/abort ",  ['b', 'e', 'a'], default = 'e', label_visibility = "hidden")
    
        email = st.text_input("Email address", value='your@email.addr', label_visibility = "hidden")

        modules = st.text_area("Modules and other initialization code", value="# module load chpc/BIOMODULES python")
    
        command = st.text_input("Command to run", value="command -switches parameters etc")
    
        if Nodes == 1:
            Queue = 'serial'
            Cores = 23
            if MPIprocs:
                MPIprocs = Cores
        elif Nodes > 20:
            Queue = 'large'
        else:
            Queue = 'normal'
        if Memory > 120 or Cores > 24 :
            Queue = 'bigmem'
    
    
        if MPIprocs != 0:
            select = "#PBS -l select={}\:ncpus={}\:mpiprocs={}\:mem={}GB".format(Nodes,Cores,MPIprocs,Memory)
        else:
            select = "#PBS -l select={}\:ncpus={}\:mem={}GB".format(Nodes,Cores,Memory)
    
        if Place and PlaceSelect:
            select = select + " -l place\:{}".format(PlaceSelect)
    
        configuration = st.form_submit_button('Write PBS script', use_container_width=True, type="primary")
    
    if configuration:
            st.write("#PBS -P " + programme)
            if email and Notify:
                st.write("#PBS -M " + email)
                st.write("#PBS -m" + ''.join(mails_on))
            st.write(select)
            st.write("PBS -q " + Queue)
            if Vars:
                st.write("PBS -V")
    
            if Interactive:
                st.write("PBS -I")
            else:
                st.write(modules)
                st.write(command)
    
