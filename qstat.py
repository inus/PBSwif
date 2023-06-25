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
                                    df['date'] = df['timestamp'].apply(lambda x: \
                                                pd.Timestamp(x, unit='s').strftime('%Y-%m-%d %H:%M:%S'))
                                    
                                    data = pd.DataFrame.from_records(df.Queue, index=df.Queue.index)
                                    pd.concat([data, pd.DataFrame.from_records(df['Queue'])])
                                    st.write(data)
                            else:
                                 st.warning("No network connection")
                        else:
                            st.error("Give a valid cluster username for ssh, not \"{}\"".format(st.session_state.user))

                st.spinner("Completed")

