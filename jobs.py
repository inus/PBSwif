# status.py
import json
import pandas as pd
import streamlit as st
from subprocess import run, TimeoutExpired

from pbs import DRMAA_avail

SSH_TIMEOUT=15

CMD = " qstat -f -w -F json -x -u $USER "
#This  ^ space is essential

def show_jobs(st, status_tab):        

    def get_drmaa_jobstats():                
            try:
                jobs = run(CMD, capture_output=True, shell=True)
            except TimeoutError:
                 st.error("Qstat failed")
                 return pd.DataFrame()            
            try:
                    df = pd.read_json(jobs.stdout.decode() )
            except:
                    df = json.loads(jobs.stdout.decode())
                    df = pd.json_normalize(df)
                    st.info("No recent queued or completed jobs found")
                    return df

            df = json.loads(jobs.stdout.decode())
            df = pd.DataFrame(df) 
            df = pd.json_normalize(df.Jobs)

            return pd.DataFrame(df)


    def get_jobstats():
        with st.spinner("Getting job data..."):
              creds = st.session_state.user + '@' + st.session_state.server 
              try:
                  qstat = run("ssh " + creds + CMD,
                               capture_output=True, shell=True,
                               timeout=SSH_TIMEOUT, check=True)      
              except TimeoutExpired:
                  st.error("Check username, ssh " + creds + " failed")
                  return pd.DataFrame()
                
              try:
                      df = pd.read_json(qstat.stdout.decode() )
              except:
                      df = json.loads(qstat.stdout.decode())
                      df = pd.json_normalize(df)
                      server = ''.join([x for x in df.pbs_server])
                      st.info("No queued or recently completed jobs on PBS " + 
                               str(server))
                      #import pdb; pdb.set_trace()
                      return df

              #df = json.loads(qstat.stdout.decode())
              df = pd.read_json(qstat.stdout.decode()) 
              df = pd.DataFrame(df) #['Jobs'])
              df = pd.json_normalize(df)
              
        st.spinner("Completed")
        return pd.DataFrame(df)

    
    with status_tab:
        if DRMAA_avail:
            df = get_drmaa_jobstats()
            st.dataframe(df)
        else:
            if st.session_state.user != "":
                df = get_jobstats()
                st.dataframe(df)
            else:
                 st.warning("Empty ssh username")

