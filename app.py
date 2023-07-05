# a streamlit app for CHPC PBS job submission

import streamlit as st

from sidebar import show_sidebar
from pbs import show_pbs
from jobs import show_jobs
from info import show_info
from shell import show_shell
from qstat import show_queue
from dash import show_dash
from setup_ssh import show_setup

st.set_page_config(    
    page_title="PBS Job Script Helper",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.header('PBS web interface')


show_sidebar(st)

placeholder = st.empty()

if st.session_state.user == "":
    with placeholder.container():
        setup_ssh = st.tabs(["Setup"])
        if show_setup(st, setup_ssh):
            placeholder.empty()
        else:
            st.stop()

dash, script, jobs, shell, queue = st.tabs(["Dash", "Script", "Jobs", "Shell", "Queue"])
show_dash(st, dash)
show_pbs(st,script)
show_jobs(st,jobs)
show_shell(st, shell)
show_queue(st, queue)

