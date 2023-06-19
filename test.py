#test.py 
import streamlit as st

import re,json
from subprocess import run
import pandas as pd

def show_test(st, test_tab):

  with test_tab:

    with st.form(key='test_form'):


            if st.session_state.use_ssh:
                creds = st.session_state.user + '@' + st.session_state.server 
                cmd = st.text_input('command to execute', key='testcmd', value='w')
        
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

