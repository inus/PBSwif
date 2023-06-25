#qstat.py 
import streamlit as st
import json
from subprocess import run, TimeoutExpired, CalledProcessError
import pandas as pd
import re
import inet
from pbs import DRMAA_avail, PBS_HOST, host
SSH_TIMEOUT=15

    

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

                        df = json.loads(qstat.stdout.decode())
                        df = pd.DataFrame(df)
                        st.dataframe(df)
                    else:
                         st.warning("No network connection")

                else:
                        if re.search ( '\s', st.session_state.user):
                                st.error("username has spaces")

                        if st.session_state.user != "" and not re.search ( '\s', st.session_state.user): 
                            creds = st.session_state.user + '@' + st.session_state.server 

                            if inet.up():

                                    qstat = get_qstat(creds, cmd)

                                    df = pd.DataFrame(json.loads(qstat.stdout.decode()))
                                    qs  = pd.Series(df.Queue.keys())

                                    q_list = []
                                    sc = df.Queue[qs[0]]['state_count'].split()
                                    header = [ x.split(':')[0] for x in sc ]
                                    for q in qs: # for every queue
                                        sd =[]
                                        sc = df.Queue[q]['state_count'].split() #all states
                                        sd += [ int(x.split(':')[1]) for x in sc ] 
                                        q_list += [sd]
                                    
                                    ql = pd.DataFrame(q_list, qs, columns=header, dtype=int)
                                    st.dataframe(ql)
                            else:
                                 st.warning("No network connection")

                        else:
                            st.error("Give a valid cluster username for ssh, not \"{}\"".format(st.session_state.user))

                st.spinner("Completed")

