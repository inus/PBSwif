#dash.py 

from glob import glob
import numpy as np
import pandas as pd
import polars as pl
import pathlib2 as pl2
import streamlit as st
from plot import plot_bokeh

from bokeh.plotting import figure
from bokeh.palettes import Spectral8 
from bokeh.models import ColumnDataSource, RangeTool, Range1d, HoverTool, Circle


import plost

LOGDIR='log/clusteruse'
Ht=560 #PLOTHEIGHT
FILEPATTERN='2023-*.log'

'''
	2023-06-06 00:05	 jobs_running=376	 jobs_queued=665	 jobs_held=0
	 jobs_exiting=0	 nodes_running=1308	 nodes_offline=645	 nodes_total=1368	 
     nodes_running_percent=95.61%	 cpu_used=15906	 cpu_total=33160	 
     cpu_percent=47.97%
'''

cols =['time', 'jobs_running', 'jobs_queued', 'jobs_held', 'jobs_exiting', 
       'nodes_running', 'nodes_offline', 'nodes_total', 'nodes_running_percent', 
       'cpu_used', 'cpu_total', 'cpu_percent' ]

cols_int = ['jobs_running', 'jobs_queued', 'jobs_held', 'jobs_exiting', 
       'nodes_running', 'nodes_offline', 'nodes_total',
       'cpu_used', 'cpu_total' ]

cols_float = [ 'nodes_running_percent', 'cpu_percent' ]

dtypes = {  #'time' : 'str', # l.datetime().str.to_datetime("%Y-%m-d %H:%M:%S") , # 'datetime',
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
    
    def redraw():
          print('Redrawing...')

    with dash:
              
              period_d = { '1d': 2, '1w': 7, '1m':30, '1y':365, 'all': 0} #read at least 2 files

              col1, col2 = st.columns([1, 2])
              with col1:
                     st.selectbox("Period", period_d.keys(), key='period', on_change=redraw())               

              with col2:            
                     st.checkbox("Add circles", key='circles')
              
              with st.spinner('Retrieving queue status'):
                     ps = pl2.Path(LOGDIR)
                     df = pl.DataFrame()

                     files = sorted(list(ps.glob(FILEPATTERN)))

                     '''
                     print("DEBUG; read files start: ", files[0])
                     print("DEBUG; read files   end: ", files[-1])
                     print("DEBUG: period :",  st.session_state.period, '\n lookup: ',period_d[st.session_state.period])
                     '''

                     s_files = files[ -period_d[st.session_state.period]::]

                     print("DEBUG; start: sfiles # ", len(s_files))

                     for p in  s_files:
                            dfs = pl.read_csv(str(p),
                                          has_header=False,
                                          new_columns=cols,
                                          try_parse_dates=True,
                                          null_values = '' )
                            
                            df = df.vstack(dfs)

                     df=df.with_columns ( pl.col(cols[1::]).str.replace(r'\D+\=(\d*\.?\d*)', "$1")) 
                     df=df.with_columns ( pl.col(cols[1::]).str.replace(r'[\%]', "")) 
                     df=df.with_columns ( pl.col(cols[1::]).str.replace('', '00')) 


                     df=df.with_columns(df.select( [ 
                            pl.col('time').cast(pl.Datetime),
                            pl.col(cols_int).cast(pl.Int32),
                            pl.col(cols_float).cast(pl.Float32) ]))
                     #df.sort('time') 
                     
                     #df=df.with_columns(pl.col('dtime') = pl.col('time').dt.strftime('%Y-%m-%d %H:%M'))
                     df.with_columns(dtime = df['time'].dt.strftime('%Y-%m-%d %H:%M'))
                     #df['dtime'] = df['time'].dt.strftime('%Y-%m-%d %H:%M')

                     tooltips = [
                            ("", "@y "),
                     ]

                     formatters={
                            '@{y}'        : 'printf' ,
                            #'@{cpu_percent}' : 'printf df["cpu_percent"]',
                            #'@{nodes_running_percent}'  : 'printf',
                     }
       

                     p = figure(
                            title='Lengau % Usage',
                            height=300,
                            x_axis_type="datetime", 
                            x_axis_location="below",
                            x_axis_label='Time',
                            y_axis_label='cpu_percent',
                            x_range=Range1d(df['time'][0], df['time'][-1]),
                            #tooltips = tooltips,
                            #hover = HoverTool(#names=hovernames,mode="vline",                                        
                     )

                     cp = p.line(df['time'], df['cpu_percent'], color='red', legend_label='CPU %',)
                     np = p.line(df['time'], df['nodes_running_percent'], legend_label='Nodes %', color='green')
                     
                     if st.session_state.circles:
                            cpc = p.circle_y(df['time'], df['cpu_percent'], color='red',legend_label="CPU")
                            npc = p.circle_x(df['time'], df['nodes_running_percent'],  color='blue', legend_label="Nodes")
                     #p.step( 'time', 'jobs_queued', source=source, color='blue', alpha=0.5, legend_label="Queued")

                     #p.circle_x( 'time', 'jobs_exiting', source=source, color='red', alpha=0.5, legend_label="Held", size=10)

                     #p.circle_x( 'time', 'jobs_held', source=source, color='black', alpha=0.5, legend_label="Exiting", size=10)


                     
                     hover = HoverTool(#names=hovernames,
                            mode="vline",                                        
                            tooltips = tooltips, 
                            #formatters=formatters,
                            renderers = [ cp, np,],
                     )


                     p.add_tools(hover)
                     st.bokeh_chart(p, use_container_width=True)


                     q = figure(
                            x_axis_type="datetime", x_axis_location="below",
                            x_range=Range1d(df['time'][0], df['time'][-1]),
                            title='Jobs',
                            x_axis_label='Time',
                            y_axis_label='Jobs',
                            height=300,
                            #tools=[HoverTool()],
                            #tooltips= tooltips,
                            #[    
                            #       #("Data point @x has the value @y"), # \n @jobs_running @jobs_queued" ),
                            #       ("Time", "$time{%F %H:%M}"),
                            #       ("Running", "$jobs_running"),
                            #       ("Queued", "$jobs_queued"),
                            #],
                            #formatters={
                            #       '@{time}'        : 'datetime', 
                            #       '@{jobs_running}': 'printf',
                            #       '@{jobs_queued}' : 'printf',
                            #}
                     )

                            #formatters={'@time': 'datetime'},
                            #)

                     hover2 = HoverTool(
                            tooltips = [                                  
                                   ("", "@y"),
                                   ("Time", "$time{%F %H:%M}"),
                                   #("CPU %", "@cpu_percent"),
                                   #("Nodes %", "@nodes_running_percent"),                                                               
                            ],
                            formatters={
                                   '@{time}'        : 'datetime',
                                   '@{cpu_percent}' : 'printf',
                                   '@{nodes_running_percent}'  : 'printf',
                            },
                            mode="vline",         
                            )
                     
                     #q.add_tools(hover2)

                     colors = ['red', 'green', 'blue', 'orange']
                     for col in job_cols:                           
                           q.line( df['time'],df[col], 
                                   color = colors[job_cols.index(col)],
                                   legend_label=col)

                     st.bokeh_chart(q, use_container_width=True)
                     

                     with st.expander('Data', ):
                            st.dataframe(df)

              st.spinner("Done")
