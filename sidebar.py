#sidepanel.py 
import os.path
import streamlit as st
import time
import sys
from subprocess import run

from common import DEFAULT_WALLTIME
from pbs import DRMAA_avail

CLUSTERHOST='scp.chpc.ac.za'

reread_jobs=False
def refresh_jobs():
     reread_jobs=True
     

def show_sidebar(st):

    with st.sidebar:

        def msg_off(place):
                place.empty()

        st.sidebar.header('PBS job settings')

        if not DRMAA_avail:
                with st.expander('Username', expanded=True):            
                    warning_place = st.empty()
                    if len(sys.argv) != 2:
                        user = st.text_input('SSH cluster username', key='user', on_change=msg_off(warning_place))
                        warning_place.warning("Set up ssh keys, test without password")
                    else:
                        user = st.text_input('SSH cluster username', key='user', value=str((sys.argv[1])))
                    cache_jobs = st.checkbox('Cache job data', key='cache_jobs',value=False)
        else:
                    who = run('whoami', capture_output=True, shell=True)
                    user = st.text_input('Cluster username', key='user', value=who.stdout.decode(), disabled=True)
             

        with st.expander('Admin options'):
                
            col1, col2 = st.columns([1, 2])
            with col1:
                admin_mode = st.checkbox('Admin', key='admin',value=False, help='Enable administrator mode')
            target_user = st.text_input('Other username', key='target_user', 
                                            help="Other username\'s jobs if in admin mode",
                                            on_change=refresh_jobs)
            with col2:
                all_jobs = st.checkbox('All user jobs', key='all_jobs',value=False, help='Get jobs from all')
                         

        with st.expander('Detail job parameters'):
        
            col1, col2 = st.columns([1, 2])

            with col1:
                Nodes = st.number_input("Nodes", value=1, key='Nodes', min_value=1, max_value=1000)
                Cores = st.selectbox("Cores",  [1,2,3,4,5,6,7,8,9,10,11,12,
                                            13,14,15,16,17,18,19,20,21,22,23,24,25,28,56], index=12, key='Cores')
                MPIprocs = st.selectbox("MPI Cores", [1,2,3,4,5,6,7,8,9,10,11,12,
                                            13,14,15,16,17,18,19,20,21,22,23,24,25,28,56], index=12, key='MPIprocs')            
                Memory = st.selectbox("Memory in GB",  [60,120,500,1000], index=1, key='Memory')
                GPUs = st.selectbox("GPUs",  [0,1,2,3,4], key='GPUs')

            with col2:     
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

        #if not DRMAA_avail:
        with st.expander('SSH Connection'):
            if DRMAA_avail:
                st.write('App running on cluster')
            use_ssh = st.checkbox('Use SSH', key='use_ssh', value=(not DRMAA_avail), disabled = DRMAA_avail)
            server= st.text_input('Host server', value=CLUSTERHOST, key='server', disabled = DRMAA_avail)  

            st.divider()

