# a streamlit app for CHPC PBS job submission

import streamlit as st
import socket

from pbs import show_pbs
from status import show_status
from common import show_info
from sidepanel import show_sidepanel
from test import show_test
from qstat import show_qstat


PBS_HOSTS = ['login1', 'login2', 'globus.chpc.ac.za']

st.set_page_config(    
    page_title="PBS-Pro Job Script Helper",
    page_icon=":leopard:",
    layout="wide",
    initial_sidebar_state="expanded",
)

host = socket.gethostname()

st.header('PBS web interface')

pbs, status, test, qstat = st.tabs(["PBS Script", "Status", "TestSSH", "Qstat"])

show_sidepanel(st)

show_pbs(st,pbs)

show_status(st,status)

show_test(st, test)

show_qstat(st, qstat)

show_info(st)

############################################################################################
