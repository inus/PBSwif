#test.py 
import streamlit as st

import re,json
from subprocess import run, CalledProcessError, TimeoutExpired

import inet
from pbs import DRMAA_avail 
import socket

SSH_TIMEOUT=15


def run_cluster_cmd(creds, cmd_dict, cmd, args):
     
    try:
        try:
            if DRMAA_avail:
                st.info("DRMAA Running " + cmd_dict[cmd] + args) 
                output = run(cmd_dict[cmd] + args, capture_output=True, 
                            shell=True, timeout=SSH_TIMEOUT, 
                            check=True)
            else: 
                st.info("SSH Running " + cmd_dict[cmd] + args) 
                output = run("ssh " + creds + ' ' +  cmd_dict[cmd] + args, 
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
    
    def cmd_options(user, args):
         
         cmd_dict = {
                'w':  'w',
                'df':  'df -h',
                'id':  "id ",
                'group':  'getent group | grep ' + user ,
                #"CHPC programmes":  "grep "  + user + " /home/userdb/programme_info.csv" ,
                "CHPC programmes":  "cat /home/userdb/programme_info.csv | grep " + user ,
                "blocked":   "cat /home/userdb/blockeduser | grep " + user,
                "allocations":   "cat /home/userdb/projects_status.csv | grep " +  args,
                'pbsnodes' : 'pbsnodes ' + args,
                #'rp' : "grep " + user + ""
                #'rp': "cat /home/userdb/projects_status.with_gpu.csv | grep -E \'" + prm + "\'" },'vrp','')        

                }
         admin_dict={
                'id':  "id " + args, #st.session_state.target_user ,
                'group':  'getent group | grep ' +  args, #st.session_state.target_user  ,
#                "CHPC programmes":  "grep "  +  st.session_state.target_user + " /home/userdb/programme_info.csv" ,
                "CHPC programmes":  "cat  /home/userdb/programme_info.csv | grep "   + args, #  st.session_state.target_user,
#                "blocked":   "grep " + st.session_state.target_user + " /home/userdb/blockeduser",
                "blocked":   "cat /home/userdb/blockeduser | grep " + args, #st.session_state.target_user,
         }
         if st.session_state.admin:
            return  admin_dict
         else:
            return cmd_dict

    with shell:
        if inet.up():

            if st.session_state.admin and st.session_state.target_user != "":
                 user = st.session_state.target_user
            else:
                 user =  st.session_state.user

            cmd_dict = cmd_options(user, '')

            col1, col2 = st.columns([1, 2])
            with col1:
                cmd = st.selectbox('Command', cmd_dict.keys(), key='testcmd', help = "Select command to run" )
            with col2:            
                cmd_args = st.text_input('command args', key='cmd_args', help = "Add optional argument, then click below to run")  


            with st.form(key='shell_form'):

                        if not DRMAA_avail:
                                creds = st.session_state.user + '@' + st.session_state.server  
                                prompt_host_label = st.session_state.server
                        else:
                                creds = ''
                                prompt_host_label = socket.gethostname()
       
                        if st.session_state.user is not None and cmd_options(user, cmd_args) is not None:

                            if st.form_submit_button( '**:green[' + st.session_state.user + '@' +
                                                     prompt_host_label +  
                                                     ' $]** ' + 
                                                     cmd_dict[cmd] + ' ' + cmd_args, 
                                                     disabled=( st.session_state.user == "" ),
                                                     help = "Add optional argument and click to run" ):
                                

                                st.text(run_cluster_cmd(creds,cmd_dict,cmd,cmd_args ))
                                
        else:
             st.warning("No network connection")
