#test.py 
import streamlit as st

import re,json
from subprocess import run, CalledProcessError, TimeoutExpired
import pandas as pd

import inet
from pbs import DRMAA_avail 

SSH_TIMEOUT=15

def show_shell(st, shell):

    def do_command(cmd):
         if cmd=='w': return 'w'
         if cmd=='id': return "id " + st.session_state.target_user
         if cmd=='df': return 'df -h'
         if cmd=='group': return 'getent group | grep ' + st.session_state.target_user 
         if cmd=="CHPCpgms": return "grep "  + st.session_state.target_user + " /home/userdb/programme_info.csv" 
         if cmd=="blocked": return  "grep "  + st.session_state.target_user + " /home/userdb/blockeduser"
         if cmd=="allocations": return  "cat /home/userdb/projects_status.csv"



    with shell:
        if inet.up():

            cmd1 = st.selectbox('Command', ('w', 'id', 'df', 'group', 'CHPCpgms', 'blocked', 'allocations'),
                                 key='testcmd' )

            with st.form(key='shell_form'):

                    #if st.session_state.use_ssh:

                        if not DRMAA_avail:
                                creds = st.session_state.user + '@' + st.session_state.server        
                                
                        cmd = do_command(st.session_state.testcmd)

                        if st.form_submit_button('**:green[$]** ' + cmd, 
                                                    disabled=( st.session_state.user == "" ) ):
                                try:
                                    try:
                                        if DRMAA_avail:
                                            output = run(cmd, capture_output=True, 
                                                     shell=True, timeout=SSH_TIMEOUT, check=True)
                                        else:
                                            output = run("ssh " + creds + ' ' +  cmd, capture_output=True, 
                                                     shell=True, timeout=SSH_TIMEOUT, check=True)                                                                            
                                    except CalledProcessError as c:
                                        st.error('Error in shell command:' + str(c))
                                        return
                                except TimeoutError as t:
                                    st.error("Shell command \"{}\" failed ".format(creds))
                                    return                                 
                                st.text(output.stdout.decode())
                    #else:
                            #st.warning("Shell is unavailable")
        else:
             st.warning("No network connection")
