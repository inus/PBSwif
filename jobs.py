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
                return 
            else:
                if st.session_state.target_user != "":
                        return ' -u ' + st.session_state.target_user             
        else:
            return ' -u ' + st.session_state.user
        
    def get_jobstats():

        def  get_ssh_jobs(creds, CMD):
            try:
                user = get_user()
                if user==None: 
                     cmd = creds + CMD
                else:
                     cmd = creds + CMD + user
                try:
                    qstat = run("ssh " + cmd,
                                capture_output=True, shell=True,
                                timeout=SSH_TIMEOUT, check=True)                     
                except CalledProcessError as c:
                    st.error('Could not run SSH command, error' + str(c))
                    return pd.DataFrame() 
            except TimeoutExpired as t:
                    st.error("Check username, ssh " + creds + " failed: " + str(t))
            return qstat


        def get_drmaa_jobs(creds, CMD):                
                
                if st.session_state.admin:
                    if st.session_state.target_user != "":
                        userarg  =  ' -u ' + st.session_state.target_user 
                    else:
                        userarg = ''
                else:
                        userarg = ' -u ' + st.session_state.user
                try:
                    jobs = run(CMD + userarg, capture_output=True, shell=True)
                except TimeoutError as t:
                    st.error("Qstat jobs via drmaa failed: " + str(t))
                    return pd.DataFrame()            
                return jobs



        if  get_user() == None: #"" and st.session_state.admin:
            msg =  "Getting job data for all users"
        else:
             msg =  "Getting job data for " + str(get_user())

        with st.spinner(msg):
            creds = st.session_state.user 
            if not DRMAA_avail:
                    creds += '@' + st.session_state.server             

            CMD = ' qstat -f -w -F json -x ' 
             
            if DRMAA_avail:
                qstat = get_drmaa_jobs(creds,CMD) 
            else:
                if st.session_state.user != "" and not re.search ( '\s', st.session_state.user): 
                    qstat = get_ssh_jobs(creds, CMD)                    
            if qstat.returncode == 0:                        
                    try:                    
                         df = json.loads(qstat.stdout.decode(), cls=LazyDecoder)
                    except: 
                         st.error("Error reading json ")
                         return pd.DataFrame() 
#                    import pdb; pdb.set_trace()
                    if 'Jobs' in df.keys():
                        return pd.DataFrame(df)
                    else:
                        return df
            else:
                st.error("Error reading job stats")

        st.spinner("Completed")            

        
    with status_tab:
        if inet.up():
            if st.session_state.user != "":
                df = get_jobstats()
            else:
                st.warning("Empty ssh username")
                return

            if len(df) > 4:
                    if 'Jobs' in df.keys():    
                            if get_user() == None: 
                                st.subheader('Showing ' + str(len(df.Jobs)) + ' jobs for all users')       
                            else:
                                st.subheader('Showing ' + str(len(df.Jobs)) + ' jobs for ' + get_user())
                            st.dataframe(pd.DataFrame(df))
            else:
                 st.info("No jobs for user " + st.session_state.target_user)

        else:
            st.warning("No network connection")

