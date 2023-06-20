#qstat.py 
import streamlit as st
import re,json
from subprocess import run
import pandas as pd
from pbs import DRMAA_avail, CLUSTER_AVAIL, host

#global saved_qstatus
#saved_qstatus = [] 

def show_qstat(st, qstat_tab):

  with qstat_tab:

    with st.form(key='qstat_form'):

        qstat = st.form_submit_button('Cluster Queue Status', use_container_width=True, type="primary")

        if qstat:
                cmd = 'qstat -Qa '
                if CLUSTER_AVAIL:
                        qstatresult = run(cmd, capture_output=True, shell=True)
                else: #ssh                         
                        if st.session_state.user != "user": #and len(saved_qstatus) == 0:
                            creds = st.session_state.user + '@' + st.session_state.server 
                            with st.spinner('Retrieving queue status'):
                                qstatresult = run("ssh " + creds + ' ' + cmd, capture_output=True,shell=True)
                            st.spinner("Completed")
                        else:
                            st.error("Give a valid cluster username for ssh, not {}".format(st.session_state.user))

                if qstatresult:
                    lines = [x.decode() for x in qstatresult.stdout.splitlines()]
                    data = [ l.split() for l in lines]                
                    if len(data) > 0:
                        dcolumns = data[0]
                        data.remove(data[0]) 
                        data.remove(data[0]) # remove ---- ---- ----
                        saved_qstat = data
                        df = pd.DataFrame(data)
                        df.columns = dcolumns                
                        st.dataframe(df, use_container_width=True)
            
 