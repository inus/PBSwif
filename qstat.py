#qstat.py 
import streamlit as st
import re,json
from subprocess import run, TimeoutExpired
import pandas as pd
from pbs import DRMAA_avail, CLUSTER_AVAIL, host


def show_qstat(st, qstat_tab):

  with qstat_tab:

    with st.form(key='qstat_form'):

        qstat = st.form_submit_button('Cluster Queue Status', 
                                       disabled=( st.session_state.user== "" ) ,
                                       type="primary")

        if qstat:
            with st.spinner('Retrieving queue status'):
                cmd = 'qstat -f -w -F json -f -Qa ' 
                if CLUSTER_AVAIL:
                        try:
                            qstatresult = run(cmd, capture_output=True, shell=True,
                                              timeout=15, check=True)
                        except TimeoutError:
                             st.error('Timed out running qstat locally on cluster node')
                else: #ssh                         
                        if st.session_state.user != "":
                            creds = st.session_state.user + '@' + st.session_state.server 
                            try:
                                qstat = run("ssh " + creds + ' ' + cmd, capture_output=True,shell=True,
                                                      check=True, timeout=15)
                            except TimeoutExpired:
                                st.error("SSH timeout getting qstat using {}".format(creds))
                                return                                 

                            df = json.loads(qstat.stdout.decode())
                            #import pdb; pdb.set_trace()
                            df = pd.DataFrame(df)
                            df = pd.json_normalize(df['Queue'])
                            #df = pd.DataFrame(df)
                            st.dataframe(df)

                        else:
                            st.error("Give a valid cluster username for ssh, not {}".format(st.session_state.user))

                st.spinner("Completed")
        '''
                    lines = [x.decode() for x in qstatresult.stdout.splitlines()] # fix to json
                    data = [ l.split() for l in lines]                
                    if len(data) > 0:
                        dcolumns = data[0]
                        data.remove(data[0]) 
                        data.remove(data[0]) # remove ---- ---- ----
                        saved_qstat = data
                        df = pd.DataFrame(data)
                        df.columns = dcolumns                
                        st.dataframe(df, use_container_width=True)
                    '''           
 