# a streamlit app for CHPC PBS job submission

import streamlit as st
import socket

from pbs import show_pbs
from status import show_status
from common import show_info
from sidepanel import show_sidepanel

PBS_HOSTS = ['login1', 'login2', 'globus.chpc.ac.za', 'Macbeth.local']

st.set_page_config(    
    page_title="CHPC PBS-Pro Job Script Helper",
    page_icon="CHPC ICON",
    layout="wide",
    initial_sidebar_state="expanded",
)

host = socket.gethostname()

pbs_tab, status_tab = st.tabs(["PBS Script", "Status"])

show_sidepanel(st)

show_pbs(st,pbs_tab)

show_status(st,status_tab)

show_info(st)

############################################################################################
