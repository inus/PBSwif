#test.py 
import streamlit as st

import re,json
from subprocess import run, CalledProcessError, TimeoutExpired

import inet
from pbs import DRMAA_avail 

SSH_TIMEOUT=15


def run_cluster_cmd(creds, cmd_dict,cmd, args):
     
    try:
        try:
            if DRMAA_avail:
                output = run(cmd_dict[cmd], capture_output=True, 
                            shell=True, timeout=SSH_TIMEOUT, 
                            check=True)
            else: 
                output = run("ssh " + creds + ' ' +  cmd_dict[cmd], 
                                capture_output=True, shell=True,
                                timeout=SSH_TIMEOUT, check=True)                                                                            
        except CalledProcessError as c:
            if c.stdout.decode() == '' :
                    st.info('No output from command \"' + cmd_dict[cmd] + '\"')
            else:
                st.error('Error in shell command: returncode ' + str(c.returncode))
            return
    except TimeoutError as t:
        st.error("Shell command \"{}\" failed ".format(creds))
        return                     
    if output.stdout.decode:            
        return output.stdout.decode()
    if output.stderr.decode():
        return output.stderr.decode()

def show_shell(st, shell):
    
    def cmd_options(user):
         
         cmd_dict = {
                'w':  'w',
                'df':  'df -h',
                'id':  "id " + user,
                'group':  'getent group | grep ' + user ,
                "CHPC programmes":  "grep "  + user + " /home/userdb/programme_info.csv" ,
                "blocked":   "grep "  + user + " /home/userdb/blockeduser",
                #"allocations":   'cat /home/userdb/projects_status.csv ' + ' | grep ' +  st.session_state.user_rp,
                'pbsnodes' : 'pbsnodes ',
                }
         return cmd_dict

    with shell:
        if inet.up():

            if st.session_state.admin and st.session_state.target_user != "":
                 user = st.session_state.target_user
            else:
                 user =  st.session_state.user

            cmd_dict = cmd_options(user)

            col1, col2 = st.columns([1, 2])
            with col1:
                cmd = st.selectbox('Command', cmd_dict.keys(), key='testcmd' )
            with col2:            
                cmd_args = st.text_input('command args', key='cmd_args')  

            with st.form(key='shell_form'):

                        if not DRMAA_avail:
                                creds = st.session_state.user + '@' + st.session_state.server  
       
                        if st.session_state.user is not None and cmd_options(user) is not None:

                            if st.form_submit_button( '**:green[' + user + '@' +
                                                     st.session_state.server +  
                                                     ' $]** ' + 
                                                     cmd_dict[cmd] + ' ' + cmd_args, 
                                                     disabled=( st.session_state.user == "" ) ):
                                

                                st.text(run_cluster_cmd(creds,cmd_dict,cmd,cmd_args ))
                                
        else:
             st.warning("No network connection")
