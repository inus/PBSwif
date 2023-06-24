# status.py
import json
import pandas as pd
import re
import streamlit as st
from subprocess import run, TimeoutExpired, CalledProcessError

from pbs import DRMAA_avail

SSH_TIMEOUT=15


def show_jobs(st, status_tab):        
    

    def get_drmaa_jobstats():                
            CMD = "qstat -f -w -F json -x -u $USER "
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
            return df


    def get_jobstats():

        @st.cache_data(persist="disk")
        def  get_ssh_jobs(creds, CMD):
                
            try:
                try:
                    qstat = run("ssh " + creds + CMD + st.session_state.user,
                                capture_output=True, shell=True,
                                timeout=SSH_TIMEOUT, check=True)                     
                except CalledProcessError as c:
                    st.error('Could not run SSH command, error' + str(c))
                    return qstat
            except TimeoutExpired as t:
                    st.error("Check username, ssh " + creds + " failed: " + str(t))

            return qstat

        with st.spinner("Getting job data for " + st.session_state.user ):
            creds = st.session_state.user + '@' + st.session_state.server 
            CMD = ' qstat -f -w -F json -x -u ' 
             
            if st.session_state.user != "" and not re.search ( '\s', st.session_state.user): 
                    qstat = get_ssh_jobs(creds, CMD)
                    
                    if qstat.returncode == 0:
                        try:                    
                                df = pd.read_json(qstat.stdout.decode() )
                        except:
                                pass

                                df = json.loads(qstat.stdout.decode())
                                df = pd.json_normalize(df)
                                server = ''.join([x for x in df.pbs_server])
                                st.info("No queued or recently completed jobs on PBS " + 
                                        str(server))
                                return pd.DataFrame()
                        
                        #df = pd.read_json(qstat.stdout.decode()) 
                        return df 
                    
                    
                    else:
                        return pd.DataFrame()
            
            if re.search ( '\s', st.session_state.user):
                 st.error("Spaces in username")                        
        st.spinner("Completed")            

        
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


