#common.py
import socket
    
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
  with st.expander("Show/hide CHPC Lengau queue information", expanded=False):
    st.markdown(table_md)

def show_email_options(st):
    print("Callback ")
    #import pdb; pdb.set_trace()
#    if  not 'Notify' in st.session_state:
#        st.session_state.Notify = True
    #else:
    #    st.session_state.Notify = not st.session_state.Notify

    #st.session_state.Notify = not Val
    #print("Callback EmailNotify",     st.session_state.EmailNotify )
    #print("Callback Notify",     st.session_state.Notify )

def Setup_form(st, programme, email,select,command,Queue,mails_on, jobname, workdir, modules):
    clear_on_submit = False

    '''
    Nodes = st.number_input("Number of nodes",value=1)
    Cores = st.selectbox("Cores", [1,2,3,4,5,6,7,8,9,10,11,12,
                                   13,14,15,16,17,18,19,20,21,22,23,24,25,28,56], index=23)
    Memory = st.selectbox("Memory in GB",  [60,120,500,1000], index=1)
    Queue = st.selectbox("Queue",  ['serial','seriallong', 'smp','normal', 'large','xlarge','bigmem',
                                    'vis','test','gpu_1','gpu_2','gpu_3','gpu_4','gpu_long','express'], 
                                    index=3)
    '''

    jobname  = st.text_input("Job name or label", value='job name')
    programme = st.text_input("Your CHPC Research Programme code", value='CHPC-RPcode')

#    Notify  = st.checkbox("Receive job emails", on_change=show_email_options(st), value=True, key='Notify2')
    if  not 'Notify' in st.session_state:
        st.session_state.Notify = True
    #else:
    #    st.session_state.Notify = not st.session_state.Notify


    email = st.text_input("Email address", value='your@email.addr')

    mails_on  = st.multiselect("Notify emails on begin/end/abort ",  ['b', 'e', 'a'], 
                               default = 'e', disabled= not(st.session_state.Notify))

    errorfile = st.text_input("Error file name - leave empty to use job-id")
    outfile = st.text_input("Output file name - leave empty to use job-id"  )
    workdir = st.text_input("Working directory")
    modules = st.text_area("Modules and other initialization code", value="# module load chpc/BIOMODULES python")
    command = st.text_input("Command to run", value="command -switches parameters etc")

    '''
    if Nodes == 1:
        Queue = 'serial'
        Cores = 23
    elif Nodes > 20:
        Queue = 'large'
    else:
        Queue = 'normal'
    if Memory > 120 or Cores > 24 :
        Queue = 'bigmem'

    select = "#PBS -l select={}\:ncpus={}\:mem={}GB".format(Nodes,Cores,Memory)
    '''


def Setup_tabs(st):
  host = socket.gethostname()
  if host in ['login1', 'login2', 'globus.chpc.ac.za']:
    simple_pbs_tab, pbs_tab, qsub_tab, status_tab = st.tabs(["Simple PBS job", "PBS job", "Qsub", "Status"])
  else:
    simple_pbs_tab, pbs_tab, status_tab = st.tabs(["Simple PBS job", "PBS job", "Status"])


def print_script(st, programme, email, select, command, queue, mails_on, jobname, Notify, modules):
            st.text("#PBS -P " + programme)
            if email and Notify:
                st.text("#PBS -M " + email)
                st.text("#PBS -m " + ''.join(mails_on))
            st.text("#PBS " + select)
            st.text("PBS -q " + queue)
            st.text("PBS -N " + jobname)
            st.text(modules)
            st.text(command)


