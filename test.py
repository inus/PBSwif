#test.py 
import streamlit as st

import re,json
from subprocess import run
import pandas as pd
from pbs import DRMAA_avail 

def show_test(st, test_tab):

  with test_tab:

    with st.form(key='test_form'):

        cmd = st.text_input('command to execute', key='testcmd', value='w')
        if not DRMAA_avail:
            if st.session_state.use_ssh:
                creds = st.session_state.user + '@' + st.session_state.server 
        
                if st.form_submit_button('Test SSH', use_container_width=True, type="primary"):

                    #try:
                    output = run("ssh " + creds + ' ' + st.session_state.testcmd, capture_output=True, shell=True) 
                    #, timeout=5.0, check=True)
                    #except subprocess.TimeoutExpired:
                    #    st.error("SSH {} failed ".format(creds))
                    #    return 

                    lines = [x.decode() for x in output.stdout.splitlines() ]

                    st.table(lines)                     

            else:
                    st.warning("SSH is disabled")

        else:
                if st.form_submit_button('Test SSH', use_container_width=True, type="primary"):
                    output = run(st.session_state.testcmd, capture_output=True, shell=True) 
                    lines = [x.decode() for x in output.stdout.splitlines() ]
                    st.table(lines)                     
                    #, timeout=5.0, check=True)



