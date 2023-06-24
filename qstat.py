#qstat.py 
import streamlit as st
import json
from subprocess import run, TimeoutExpired, CalledProcessError
import pandas as pd
import re
from pbs import DRMAA_avail, CLUSTER_AVAIL, host
SSH_TIMEOUT=15

def show_queue(st, queue):

  
  
    @st.cache_data(persist="disk")
    def get_qstat(creds, cmd):


        try:

            try:
                    qstat = run("ssh " + creds + ' ' + cmd, capture_output=True,shell=True,
                                        check=True, timeout=SSH_TIMEOUT)
                    
            except CalledProcessError as c:
                st.error('Could not run SSH command, error' + c,output.decode())
                return

        except TimeoutExpired:
                st.error("SSH timeout getting qstat using {}".format(creds))
                return
        return qstat                                 



    with queue:
        with st.form(key='qstat_form'):
            with st.spinner('Retrieving queue status'):
                cmd = 'qstat -f -w -F json -f -Qa ' 
                if CLUSTER_AVAIL:

                        qstat_btn = st.form_submit_button('Cluster Queue Status', 
                                       disabled=True)

                        try:
                            qstat = run(cmd, capture_output=True, shell=True,
                                              timeout=15, check=True)
                        except TimeoutError:
                             st.error('Timed out running qstat locally on cluster node')

                        df = pd.read_json(qstat.stdout.decode())
                        df = pd.DataFrame(df)
                        df = pd.json_normalize(df['Queue'])
                        st.dataframe(df)

                else:

                        qstat = st.form_submit_button('Cluster Queue Status', 
                                       disabled=( st.session_state.user== "" ) ,
                                       type="primary")
                        if re.search ( '\s', st.session_state.user):
                                st.error("username has spaces")

                        if st.session_state.user != "" and not re.search ( '\s', st.session_state.user): 
                            creds = st.session_state.user + '@' + st.session_state.server 

                            qstat = get_qstat(creds, cmd)

                            df = pd.DataFrame(json.loads(qstat.stdout.decode()))
                            qs  = pd.Series(df.Queue.keys())


                            q_list = []
                            sc = df.Queue[qs[0]]['state_count'].split()
                            header =  [x.split(':')[0] for x  in sc]
                            for q in qs: # for every queue
                                sd =[]
                                sc = df.Queue[q]['state_count'].split() #all states
                                sd += [ int(x.split(':')[1]) for x  in sc] 
                                q_list += [ sd]
                            
                            ql = pd.DataFrame(q_list, qs, columns=header, dtype=int)
                            st.dataframe(ql)

                        else:
                            st.error("Give a valid cluster username for ssh, not \"{}\"".format(st.session_state.user))

                st.spinner("Completed")

