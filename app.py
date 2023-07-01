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
from dash import show_dash

st.set_page_config(    
    page_title="PBS Job Script Helper",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header('PBS web interface')

dash, script, jobs, shell, queue = st.tabs(["Dash", "Script", "Jobs", "Shell", "Queue"])

show_sidebar(st)

show_dash(st, dash)

show_pbs(st,script)

show_jobs(st,jobs)

show_shell(st, shell)

show_queue(st, queue)
