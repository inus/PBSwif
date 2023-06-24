# a streamlit app for CHPC PBS job submission

import streamlit as st
import socket
import sqlite3
import sys
from sidebar import show_sidebar

from pbs import show_pbs
from jobs import show_jobs
from info import show_info
from shell import show_shell
from qstat import show_queue

st.set_page_config(    
    page_title="PBS Job Script Helper",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header('PBS web interface')

script, jobs, shell, queue = st.tabs(["Script", "Jobs", "Shell", "Queue"])

show_sidebar(st)

show_pbs(st,script)

show_jobs(st,jobs)

show_shell(st, shell)

show_queue(st, queue)

show_info(st)

############################################################################################
