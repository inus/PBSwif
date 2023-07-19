#qstat.py aka queue.py 

import streamlit as st
import json
from subprocess import run, TimeoutExpired, CalledProcessError
import pandas as pd
import re
import inet
from bokeh.plotting import figure, show
from bokeh.palettes import Spectral8 


from pbs import PBS_HOST
SSH_TIMEOUT=15

def queue_graph(data):

    state_names = ['Transit', 'Queued', 'Held', 'Waiting', 'Running', 'Exiting', 'Begun' ]
    queues = list(data.index)
    states = {} 
    for q in queues:        
        state_count = [ int(x.split(':')[1]) for x in  data.state_count[q].split() ]
        states[q] = state_count

    data = { 'Queue': queues,
             'States': state_names,
             'Counts': states}

    df = pd.DataFrame.from_records(data['Counts'], columns=queues, index=state_names) 
    df.reindex()
    plot=[]
    for q in queues: plot += [df[q]]
    st.bar_chart(plot)

    
def show_queue(st, queue):
  
    @st.cache_data(persist="disk")
    def get_qstat(creds, cmd):

        try:
            try:
                    qstat = run("ssh " + creds + ' ' + cmd, capture_output=True,shell=True,
                                        check=True, timeout=SSH_TIMEOUT)                    
            except CalledProcessError as c:
                    st.error('Could not run SSH command, error' + c.output.decode())
                    return
        except TimeoutExpired:
                st.error("SSH timeout getting qstat using {}".format(creds))
                return
        return qstat                                 


    with queue:
            with st.spinner('Retrieving queue status'):
                cmd = 'qstat -f -w -F json -f -Qa ' 
                if PBS_HOST:
                    if inet.up():
                        try:
                            qstat = run(cmd, capture_output=True, shell=True,
                                              timeout=SSH_TIMEOUT, check=True)
                        except TimeoutError:
                             st.error('Timed out running qstat on cluster')

                        df = pd.DataFrame(json.loads(qstat.stdout.decode()))
                        df = pd.DataFrame.from_records(df.Queue, index=df.Queue.index)
                        queue_graph(df)
                    else:
                         st.warning("No network connection")

                else:
                        if re.search ( '\s', st.session_state.user):
                                st.error("username has spaces")

                        if st.session_state.user != "" and not re.search ( '\s', st.session_state.user): 
                            creds = st.session_state.user + '@' + st.session_state.server 
                            if inet.up():
                                    qstat = get_qstat(creds, cmd)
                                    if qstat is None:
                                         st.error('No queue data')
                                    else:

                                        df = pd.DataFrame(json.loads(qstat.stdout.decode()))
                                        df['date'] = df['timestamp'].apply(lambda x: \
                                                    pd.Timestamp(x, unit='s').strftime('%Y-%m-%d %H:%M:%S'))
                                        
                                        data = pd.DataFrame.from_records(df.Queue, index=df.Queue.index)
                                        pd.concat([data, pd.DataFrame.from_records(df['Queue'])])
                                        #pdf = pd.DataFrame(json.loads(qstat.stdout.decode()))
                                        queue_graph(data)
                                        q_info = data[['Priority', 'queue_type', 'enabled',  'default_chunk','started' ]]
                                        q_res = data[['resources_assigned', 'resources_max', 
                                                      'resources_min', 'max_run_res', ]]
                                        q_acl = data[['acl_group_enable', 'acl_groups', 'acl_users',]]

                                        with st.expander("Queue info"): st.dataframe(q_info)
                                        with st.expander("Queue resources"): st.dataframe(q_res)
                                        with st.expander("Queue ACL "): st.dataframe(q_acl)
                                        
                            else:
                                 st.warning("No network connection")
                        else:
                            st.error("Give a valid cluster username for ssh, not \"{}\"".format(st.session_state.user))

                st.spinner("Completed")

