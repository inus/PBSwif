# status.py
import json
import os
import pandas as pd
import re
import streamlit as st
from subprocess import run, TimeoutExpired
from pbs import DRMAA_avail

global saved_jobids
saved_jobids= []


def show_status(st, status_tab):        

    df_all = pd.DataFrame()

    def get_drmaa_jobstats():                

            CMD = "qstat -f -w -F json -x -u $USER "
            try:
                jobs = run(CMD,capture_output=True,shell=True)
            except TimeoutError:
                 st.error("Qstat failed")
                 return pd.DataFrame()            
            try:
                    df = pd.read_json(jobs.stdout.decode() )
            except:
                    df = json.loads(jobs.stdout.decode())
                    ndf = pd.json_normalize(df)
                    st.info("No recent queued or completed jobs found")
                    return ndf

            df = pd.read_json(jobs.stdout.decode() )
            df = json.loads(jobs.stdout.decode())
            ndf = pd.json_normalize(df.Jobs)

            return pd.DataFrame(ndf)

    def get_ssh_jobdetails(jobid):

        creds = st.session_state.user + '@' + st.session_state.server 
        CMD = 'qstat -x -f -F json -w  -u $USER ' +  str(jobid)
        try: 
            qstat = run("ssh " + creds + ' ' + CMD, capture_output=True, shell=True, timeout=5, check=True) 
        except TimeoutError:
             st.error("Check username, ssh " + creds + " failed")
             return pd.DataFrame
        jsondata = json.loads(qstat.stdout.decode())
        jdf = pd.DataFrame(jsondata)
        ndf = pd.json_normalize(jdf.Jobs )
        ndf.insert(0, 'Job ID', jobid)
        return pd.DataFrame(ndf)



    def get_jobstats():
        with st.spinner("Getting job data..."):
              creds = st.session_state.user + '@' + st.session_state.server 
              CMD = 'qstat -x -F json -f -w -u ' + st.session_state.user 
              try:
                  qstat = run("ssh " + creds + ' ' + CMD, capture_output=True, shell=True, timeout=8, check=True)      
              except TimeoutExpired:
                  st.error("Check username, ssh " + creds + " failed")
                  return pd.DataFrame()
              jdf = pd.read_json(qstat.stdout.decode())
              ndf = pd.json_normalize(jdf.Jobs)
              df = pd.DataFrame(ndf)
        st.spinner("Completed")
        return df

    
    with status_tab:
        if DRMAA_avail:
            df = get_drmaa_jobstats()
            st.dataframe(df)
        else:
            if st.session_state.user != "":
                df = get_jobstats()
                st.dataframe(df)
           # else:
           #     st.error("No recent jobs found")


