#common.py
import socket
import streamlit as st

DEFAULT_WALLTIME=48

global jobs_retrieved 
#jobs_retrieved  = False

#Lengau queue specs from https://wiki.chpc.ac.za    
table_md = """
| Queue Name         | Min nodes/job| Min cores/job |Max nodes/job  | Max cores/job  | Max jobs in Q   | Max jobs running   |  Max time (h) |   Notes  | Access  |
| ---                | ---          | ---           |---            | ---            | ---             | ---                | ---           |  ---     |   ---   |
| serial             |    1         |    1          |   1           |     23         |  24 |  10       |  48 | For single-node non-parallel jobs.  |  |
| seriallong         |    1         |    1          |   1           |     12         |  24 |  10       | 144 | For very long sub 1-node jobs.  |  |
| smp                |    1         |   24          |   1           |     24         |  20 |  10       |  96 | For single-node parallel jobs.  |  |
| **:green[normal]** |    2         |   25          |  10           |    240         |  20 |  10       |  48 | The standard queue for parallel jobs   |
| large              |   11         |  264          |1000           |   2400         |  10 |  5        |  96 | For large parallel runs  | Restricted  |
| xlarge             | 1001         | 2424          | 250           |   6000         |  2  |  1        |  96 | For extra-large parallel runs  | Restricted  |
| bigmem             |    1         |   28          |   5           |    280         |  4  |  1        |  48 | For the large memory (1TiB RAM) nodes. | Restricted  |
| vis                |    1         |    1          |   1           |     12         |  1  |  1        |  3  | Visualisation node  |  |
| test               |    1         |    1          |   1           |     24         |  1  |  1        |  3  | Normal nodes, for testing only  |  |
| gpu_1              |    1         |    1          |   1           |     10         |     |  2        |  12 | Up to 10 cpus, 1 GPU        |  |
| gpu_2              |    1         |    1          |   1           |     20         |     |  2        |  12 | Up to 20 cpus, 2 GPUs        |  |
| gpu_3              |    1         |    1          |   1           |     36         |     |  2        |  12 | Up to 36 cpus, 3 GPUs        |  |
| gpu_4              |    1         |    1          |   1           |     40         |     |  2        |  12 | Up to 40 cpus, 4 GPUs        |  |
| gpu_long           |    1         |    1          |   1           |     20         |     |  1        |  24 | Up to 20 cpus, 1 or 2 GPUs        |  Restricted |
| **:red[express]**  |    2         |   25          | 100           |   2400         |     | 100 nodes |  96 | For paid commercial use only  | Restricted  |
"""

def show_info(st):
  with st.expander("Show/hide CHPC Lengau PBS queue rules", expanded=False):
    st.markdown(table_md)

def show_email_options(st):
    print("Callback ")
    if  'Notify' in st.session_state:
        st.session_state.Notify = not st.session_state.Notify

def check_select(st): 

    Nodes, Cores, Memory, Queue, MPIprocs, GPUs, walltime = st.session_state.Nodes, \
        st.session_state.Cores, st.session_state.Memory, st.session_state.Queue, \
        st.session_state.MPIprocs, st.session_state.GPUs, st.session_state.walltime

    if Nodes == 1:
        if GPUs > 0:
            Queue = 'gpu_' + str(GPUs)
        else:
            if Memory > 120:
                Queue = 'bigmem'
                if walltime > 48: walltime = 48
            else:
                if Cores == 24:
                    Queue = 'smp'
                    if walltime > 96: walltime = 96
                else:
                    if walltime > 96: 
                        Queue = 'seriallong'
                        if walltime > 144: walltime = 144
                    else:
                        Queue = 'serial'
                        if walltime > 48: walltime = 48


    elif Nodes >= 2:
        if Cores < 24: 
            Cores = 24
        Queue = 'normal'
        if walltime > 48: walltime = 48

    elif Nodes > 20:     # TODO: Check queue limits with Qstat            
        Queue = 'large'
        if walltime > 96: walltime = 96

    else:
        Queue = 'normal'
        if walltime > 48: walltime = 48

    if GPUs > 0:
        if GPUs == 1 : 
            if Cores > 10: Cores = 10
        if GPUs == 2 : 
            if Cores > 20: Cores = 20
        if GPUs == 3 : 
            if Cores > 36: Cores = 36
        if GPUs == 4 : 
            if Cores > 40: Cores = 40
        if MPIprocs > Cores:
            MPIprocs = Cores
        if walltime > 12:
            walltime = 12

        select = "-l select={}:ncpus={}:ngpus={}:mpiprocs={}:mem={}GB".format(Nodes,Cores,GPUs,MPIprocs,Memory)

    else:  #no GPU      
        if MPIprocs != 0:
            if MPIprocs > Cores: MPIprocs = Cores            
            select = "-l select={}:ncpus={}:mpiprocs={}:mem={}GB".format(Nodes,Cores,MPIprocs,Memory)
        else:
            select = "-l select={}:ncpus={}:mem={}GB".format(Nodes,Cores,Memory)
    
    if st.session_state.PlaceSelect != "none":
        select = select + " -l place={}".format(st.session_state.PlaceSelect)

    if st.session_state.walltime != DEFAULT_WALLTIME:
        select = select + " -l walltime=" + str(st.session_state.walltime) + ':' + str(st.session_state.walltime_m) 

    return select, Nodes, Cores, Memory, Queue, MPIprocs, GPUs


def save_settings():
    fp = open('settings.conf', 'w')
    fp.write('sshuser=' + st.session_state.sshuser)
    fp.write('programme=' + st.session_state.programme)
    fp.close()

def read_settings():
    fp = open('settings.conf',)
#    fp.read('sshuser=' + st.session_state.sshuser)
#    fp.write('programme=' + st.session_state.programme)
#    fp.close()
