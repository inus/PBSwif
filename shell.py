#test.py 
import streamlit as st

import re,json
from subprocess import run
import pandas as pd
from pbs import DRMAA_avail 

SSH_TIMEOUT=15

def show_shell(st, shell):

  with shell:

    with st.form(key='shell_form'):

        cmd = st.text_input('command to execute', key='testcmd', value='w')
        if not DRMAA_avail:
            if st.session_state.use_ssh:
                creds = st.session_state.user + '@' + st.session_state.server 
                        
                if st.form_submit_button('Test SSH', type="primary",
                                             disabled=( st.session_state.user == "" ) ):
                        try:
                            output = run("ssh " + creds + ' ' + st.session_state.testcmd,
                                    capture_output=True, shell=True, timeout=SSH_TIMEOUT, check=True)
                        except TimeoutError as t:
                            st.error("SSH {} failed ".format(creds))
                            return 

                        lines = [x.decode() for x in output.stdout.splitlines()]
                        for l in lines:
                            st.text(l)

            else:
                    st.warning("SSH is disabled")

        else:
                if st.form_submit_button('Test SSH', type="primary"):
                    try:
                            output = run(st.session_state.testcmd, capture_output=True, shell=True) 
                    except TimeoutError:
                         st.error("SSH timeout")
                         return
                    
                    lines = [x.decode() for x in output.stdout.splitlines() ]
                    for l in lines:
                         st.text(l)



