# a streamlit app for CHPC PBS job submission
import streamlit as st
import socket

#from pbs_simple import show_simple_pbs
from pbs import show_pbs
from qsub import show_qsub
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

#if host in PBS_HOSTS:
#simple_pbs_tab, pbs_tab, qsub_tab, status_tab = st.tabs(["Simple PBS job", "PBS job", "Qsub", "Status"])
#else:
pbs_tab, qsub_tab, status_tab = st.tabs(["Script", "QSub", "Status"])

show_sidepanel(st)
#show_simple_pbs(st,simple_pbs_tab)  

show_pbs(st,pbs_tab)

#if host in PBS_HOSTS:
show_qsub(st,qsub_tab)

show_status(st,status_tab)

show_info(st)

############################################################################################
