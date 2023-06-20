# a streamlit app for CHPC PBS job submission

import streamlit as st
import socket
import sqlite3

from sidepanel import show_sidepanel

from pbs import show_pbs
from status import show_status
from common import show_info
from test import show_test
from qstat import show_qstat

st.set_page_config(    
    page_title="PBS-Pro Job Script Helper",
    page_icon=":leopard:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header('PBS web interface')

pbs, status, test, qstat = st.tabs(["PBS Script", "Job Status", "Shell", "Qstat"])

show_sidepanel(st)

show_pbs(st,pbs)

show_status(st,status)

show_test(st, test)

show_qstat(st, qstat)

show_info(st)

############################################################################################
