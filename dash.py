#dash.py 

from glob import glob
import numpy as np
import pandas as pd
import pathlib2 as pl2
import streamlit as st
from plot import plot_bokeh

import plost

LOGDIR='log/clusteruse'
Ht=560 #PLOTHEIGHT
FILEPATTERN='2023-06-2?.log'

'''
	2023-06-06 00:05	 jobs_running=376	 jobs_queued=665	 jobs_held=0
	 jobs_exiting=0	 nodes_running=1308	 nodes_offline=645	 nodes_total=1368	 
     nodes_running_percent=95.61%	 cpu_used=15906	 cpu_total=33160	 
     cpu_percent=47.97%
'''

cols =['time', 'jobs_running', 'jobs_queued', 'jobs_held', 'jobs_exiting', 
       'nodes_running', 'nodes_offline', 'nodes_total', 'nodes_running_percent', 
       'cpu_used', 'cpu_total', 'cpu_percent' ]

dtypes = { 'time' : 'object',
          'jobs_running': 'int', 'jobs_queued': 'int', 'jobs_held': 'int', 'jobs_exiting': 'int',
          'nodes_running': 'int', 'nodes_offline': 'int', 'nodes_total': 'int',
          'nodes_running_percent': 'float', 
          'cpu_used': 'int', 'cpu_total': 'int', 'cpu_percent': 'float' }

icols =['jobs_running', 'jobs_queued', 'jobs_held', 'jobs_exiting', 
       'nodes_running', 'nodes_offline', 'nodes_total',
       'cpu_used', 'cpu_total', ]

fcols=['nodes_running_percent', 
       'cpu_percent' ]


job_cols =['jobs_running', 'jobs_queued', 'jobs_held', 'jobs_exiting', ]
node_cols=['nodes_running', 'nodes_offline', 'nodes_total', 'nodes_running_percent',]
cpu_cols =['cpu_used', 'cpu_total', 'cpu_percent' ]

num_cols =['jobs_running', 'jobs_queued', 'jobs_held', 'jobs_exiting', 
       'nodes_running', 'nodes_offline', 'nodes_total', 'nodes_running_percent', 
       'cpu_used', 'cpu_total', 'cpu_percent' ]


def show_dash(st, dash):

    with dash:
            with st.spinner('Retrieving queue status'):
                    ps = pl2.Path(LOGDIR)
                    df = pd.DataFrame()
                    for p in  ps.glob(FILEPATTERN):
                        dfs = pd.read_csv(p, names=cols).fillna(0)
                        df = pd.concat((df, dfs))

                    df[cols] = df[cols].replace(r'\w+\=(\d*\.?\d*)',r'\1', regex=True)     

                    df[fcols] = df[fcols].replace(r'[\%]','', regex=True)

                    df[cols] = df[cols].replace(r' ', 0)
                    df[cols] = df[cols].replace(r' ', np.nan)

                    df.fillna(df.median(numeric_only=True).round(1), inplace=True)

                    df.time = pd.to_datetime(df.time)
                    if np.any(df.time)==0:
                         print("DEBUG - zero date")

                    for c in num_cols:
                       pd.to_numeric(df[c]) 
                    plot_bokeh(df)

                    st.write(df)
#                    plot_df = pd.DataFrame(df.queue)
                    #plost.bar_chart(data=df, bar=icols, value=icols)


            st.spinner("Done")
