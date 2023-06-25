# jobs.py
import json
import pandas as pd
import re
import streamlit as st
from subprocess import run, TimeoutExpired, CalledProcessError
import inet
from pbs import DRMAA_avail

SSH_TIMEOUT=15

class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)

def show_jobs(st, status_tab):  

    def  get_user():
        if st.session_state.admin:
            if st.session_state.all_jobs:
                return str('')
            else:
                if st.session_state.target_user == "":
                        st.warning('No username ')
                else:
                        return ' -u ' + st.session_state.target_user             
        else:
            return ' -u ' + st.session_state.user
        
    def get_drmaa_jobstats():                
            CMD = "qstat -f -w -F json -x -u $USER "
            try:
                jobs = run(CMD, capture_output=True, shell=True)
            except TimeoutError:
                 st.error("Qstat failed")
                 return pd.DataFrame()            
            try:
                    df = json.load(jobs.stdout.decode(), cls=LazyDecoder)
            except:
                    df = json.loads(jobs.stdout.decode(), )
                    df = pd.json_normalize(df)
                    st.info("No recent queued or completed jobs found")
                    return df

            df = json.loads(jobs.stdout.decode(), cls=LazyDecoder)
            df = pd.DataFrame(df) 
            df = pd.json_normalize(df.Jobs)
            return df


    def get_jobstats():

        #@st.cache_data(persist=st.session_state.cache_jobs)
        def  get_ssh_jobs(creds, CMD):
            try:
                user = get_user()
                try:
                    qstat = run("ssh " + creds + CMD + user,
                                capture_output=True, shell=True,
                                timeout=SSH_TIMEOUT, check=True)                     
                except CalledProcessError as c:
                    st.error('Could not run SSH command, error' + str(c))
                    return pd.DataFrame(c) 
            except TimeoutExpired as t:
                    st.error("Check username, ssh " + creds + " failed: " + str(t))
            return qstat


        if get_user() == "" and st.session_state.admin:
            msg =  "Getting job data for all users"
        else:
             msg =  "Getting job data for " + str(get_user())

        with st.spinner(msg):
            creds = st.session_state.user + '@' + st.session_state.server             
            CMD = ' qstat -f -w -F json -x ' 
             
            if st.session_state.user != "" and not re.search ( '\s', st.session_state.user): 
                    qstat = get_ssh_jobs(creds, CMD)                    
                    if qstat.returncode == 0:                        
                        try:                    
                                df = json.loads(qstat.stdout.decode(), cls=LazyDecoder)
                        except : 
                                st.error("Error reading json ")
                                return pd.DataFrame() 
                        return df #.Jobs.explode()                                         
                    else:
                        return pd.DataFrame()
            
            if re.search ( '\s', st.session_state.user):
                 st.error("Spaces in username")                        
        st.spinner("Completed")            

        
    with status_tab:
        if inet.up():
            if DRMAA_avail:
                df = get_drmaa_jobstats()
            else:
                if st.session_state.user != "":
                    df = get_jobstats()
                else:
                    st.warning("Empty ssh username")
                    return

            #if len(pd.DataFrame(df)) > 0:
            if 'Jobs' in df.keys():    
                if get_user() != "":
                    st.subheader('Showing ' + str(len(pd.DataFrame(df))) 
                             + ' jobs for ' + get_user().split()[1])
                else:
                    st.subheader('Showing ' + str(len(pd.DataFrame(df))) 
                             + ' jobs for all users')
                st.dataframe(pd.DataFrame(df))
            else:
                 st.info("No jobs for user " + st.session_state.target_user)

        else:
            st.warning("No network connection")

