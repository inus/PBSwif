#qstat.py 
import streamlit as st
import re,json
from subprocess import run
import pandas as pd
from pbs import DRMAA_avail, CLUSTER_AVAIL, host


def show_qstat(st, qstat_tab):

  with qstat_tab:

    with st.form(key='qstat_form'):

        qstat = st.form_submit_button('Cluster Queue Status', use_container_width=True, type="primary")
        if qstat:
                
                #st.empty.write("Empty")
#    for seconds in range(60):
#        st.write(f"⏳ {seconds} seconds have passed")
#        time.sleep(1)
#    st.write("✔️ 1 minute over!")
            #with st.spinner("Running qstat on cluster"):

                cmd = 'qstat -Qa '
                if CLUSTER_AVAIL:
                    try:
                        print("DEBUG: call " + cmd )

                        qstatresult = run(cmd, capture_output=True, shell=True) #, timeout=15.0, check=true)
                    except:
                        st.error("Failed qstat on local host {}".format(host))
                        return 
                else: #ssh                         
                        if st.session_state.user != "user":
                            creds = st.session_state.user + '@' + st.session_state.server 
                            #with st.spinner('Retrieving queue status'):
                            try:
                                print("DEBUG: call qstat ssh" + cmd )
                                qstatresult = run("ssh " + creds + ' ' + cmd, capture_output=True,
                                                   shell=True) #, timeout=15.0)
                            except:
                                st.error("SSH qstat {} failed ".format(creds))
                                return 
                            #st.success('Done!')    
                        else:
                            st.error("Give a valid cluster username for ssh, not {}".format(st.session_state.user))

                if qstatresult:
                  lines = [x.decode() for x in qstatresult.stdout.splitlines()]
                  data = [ l.split() for l in lines]

                  if len(data) > 0:
                    dcolumns = data[0]
                    data.remove(data[0]) 
                    data.remove(data[0]) # remove ---- ---- ----
                    df = pd.DataFrame(data)
                    df.columns = dcolumns                
                    st.dataframe(df, use_container_width=True)
            #st.spinner("Completed")
 