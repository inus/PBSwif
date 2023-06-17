#sidepanel.py 
from common import DEFAULT_WALLTIME

def show_sidepanel(st):

    st.sidebar.header('PBS job settings')

    with st.sidebar:

        #Notify  = st.checkbox("Send email", value=True, key="Notify", ) 
        st.session_state.Notify=True

        col1, col2 = st.columns([1, 2])

        with col1:
            Nodes = st.number_input("Nodes",value=1, key='Nodes')
            Cores = st.selectbox("Cores",  [1,2,3,4,5,6,7,8,9,10,11,12,
                                        13,14,15,16,17,18,19,20,21,22,23,24,25,28,56], index=22, key='Cores')
            MPIprocs = st.selectbox("MPI Cores", [1,2,3,4,5,6,7,8,9,10,11,12,
                                        13,14,15,16,17,18,19,20,21,22,23,24,25,28,56], index=22, key='MPIprocs')
        
            Memory = st.selectbox("Memory in GB",  [60,120,500,1000], index=1, key='Memory')
            GPUs = st.selectbox("GPUs",  [0,1,2,3,4], key='GPUs')


        with col2:     

            #Place  = st.checkbox("Select job placement", key='Place', label_visibility='collapsed')
            PlaceSelect = st.selectbox("Placement", ["none", "free", "excl"], key='PlaceSelect')

            Interactive  = st.checkbox("Interactive", key="Interactive")
            Vars  = st.checkbox("Keep env vars", key="Vars")
            Xfwd  = st.checkbox("Forward X", key="Xfwd")
            CPUtype = st.selectbox("CPU type", ['haswell','haswell_fat',], key='cputype')

        
        timecol1, timecol2 = st.columns([1,1])
        with timecol1:
            walltime = st.number_input('Walltime h', value=DEFAULT_WALLTIME, key='walltime' )
        with timecol2:
            walltime_m = st.number_input('Walltime min', value=0, key='walltime_m' )

        Queue = st.selectbox("Queue",  ['serial','seriallong', 'smp','normal', 'large','xlarge','bigmem',
                                        'vis','test','gpu_1','gpu_2','gpu_3','gpu_4','gpu_long','express'], index=0,
                                        key='Queue')
        st.divider()




