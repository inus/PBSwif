#qstat.py 
import streamlit as st

import re,json
from subprocess import run
import pandas as pd
from pbs import DRMAA_avail

def show_qstat(st, _qstat_tab):

  with _qstat_tab:

    with st.form(key='qstat_form'):

        if st.session_state.user  != "user":
            qstat = st.form_submit_button('Cluster Job Queue Status', use_container_width=True, type="primary")
        else:           
            st.error("Invalid SSH username")    
            qstat = st.form_submit_button('Qstat', use_container_width=True, type="primary",
                                           disabled=True)
            return
        
        if qstat:

            if st.session_state.use_ssh and not DRMAA_avail:
                creds = st.session_state.user + '@' + st.session_state.server 
                cmd = 'qstat -Qa '

                if st.session_state.user != "user":
                    try:
                        qstat = run("ssh " + creds + ' ' + cmd, capture_output=True, shell=True)
                    except:
                        st.error("SSH Qstat {} failed ".format(creds))
                        return 
                else:
                    st.error("Give a valid cluster username, not {}".format(st.session_state.user))
                
            elif DRMAA_avail:
                try:
                    qstat = run(cmd, capture_output=True, shell=True)
                except:
                    st.error("Qstat {} failed ".format(creds))
                    return 

            lines = [x.decode() for x in qstat.stdout.splitlines()]
            data = [ l.split() for l in lines]

            if len(data) > 0:
                dcolumns = data[0]
                data.remove(data[0]) 
                data.remove(data[0]) # remove ---- ---- ----
                df = pd.DataFrame(data)
                df.columns = dcolumns                
                st.dataframe(df, use_container_width=True)
 