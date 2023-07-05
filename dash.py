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
from bokeh.models import ColumnDataSource, RangeTool,\
       Range1d, HoverTool, Circle, LinearAxis 


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

dtypes = {'jobs_running': 'int', 'jobs_queued': 'int', 
          'jobs_held': 'int', 'jobs_exiting': 'int',
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
          print('Redrawing selectbox') # st.session_state.graph_period)
    def sb_period(x):
          if x=='1d': return '1 Day'
          if x=='1w': return '1 Week'
          if x=='1m': return '1 Month'
          if x=='1y': return '1 Year'
          return x
          print('Debug sb period',x )

    with dash:
              
              period_d = { '1d': 2, '1w': 7, '1m':30, '1y':365, 'all': 0} #read at least 2 files

              col1, col2 = st.columns([1, 2])
              with col1:
                     st.selectbox("Period", period_d.keys(), key='graph_period',
                                   index=0, format_func=sb_period, on_change=redraw())               

              with col2:            
                     st.checkbox("Show node counts", key='graph_nodes')
       
                     col3, col4 = st.columns(2)
                     with col3:
                            placeholder_1 = st.empty()
                     with col4:
                            placeholder_2 = st.empty()

              
              with st.spinner('Retrieving queue status'):
                     ps = pl2.Path(LOGDIR)
                     df = pl.DataFrame()

                     files = sorted(list(ps.glob(FILEPATTERN)))

                     s_files = files[ -period_d[st.session_state.graph_period]::]


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
                     
                     df.with_columns(dtime = df['time'].dt.strftime('%Y-%m-%d %H:%M'))

                     #print("DEBUG; before ", df.shape)
                     #placeholder_1.write(files[0])


                     if  st.session_state.graph_period == '1m': #
                            every = '1h'
                     elif st.session_state.graph_period == '1y':
                            every = '4h'
                     elif st.session_state.graph_period == 'all':
                            every = '24h'
                     else:
                            every = ''

                     if every != '':

                            
                            df = df.with_columns(pl.col('time').set_sorted()).groupby_dynamic(
                                                               'time',
                                                               every=every,
                                                               check_sorted=False,
                                                               #period='2h'    #<<< TBD
                                                        ).agg(
                                                          pl.all().exclude(
                                                               'time','dtime').mean()
                                                        )
                            

                     placeholder_1.write("From: " + str(df['time'][0]))
                     placeholder_2.write("To: " + str(df['time'][-1]))

                     tooltips = [
                            ("", "@y "),
                            #("Values","$cpu_percent"),
                            #('', ""),
                            #('', "$y2 "),
                            
                            #("cpu>", "@cpu_percent"),
                            #('X2', "$y2")
                     ]

                     formatters={
                            '@{y}'        : 'printf' ,
                            '@{x}'        : 'printf',
                            #'@{$cpu_percent}'        : 'printf',
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
                     )

                     cp = p.line(df['time'], df['cpu_percent'], color='red', legend_label='CPU %',)
                     np = p.line(df['time'], df['nodes_running_percent'], legend_label='Nodes %', color='green')

                     if st.session_state.graph_nodes:
                            p.extra_y_ranges['nodes'] = Range1d(df['nodes_running'].min(), df['nodes_running'].max())
                            nr = p.line(df['time'], df['nodes_running'], color="blue", y_range_name='nodes', legend_label='Nodes running')
                            no = p.line(df['time'], df['nodes_offline'], color="orange", y_range_name='nodes', legend_label='Nodes offline')

                            ax2 = LinearAxis(y_range_name="nodes", axis_label="Nodes running")
                            ax2.axis_label_text_color ="navy"
                            p.add_layout(ax2, 'right')
                            p.y_range=Range1d(0,100)


#                     if st.session_state.circles:
#                            cpc = p.circle_y(df['time'], df['cpu_percent'], color='red',legend_label="CPU")
#                            npc = p.circle_x(df['time'], df['nodes_running_percent'],  color='blue', legend_label="Nodes")

                     if st.session_state.graph_nodes:
                            renderers = [ cp, np, nr, no]
                     else:
                            renderers = [ cp, np, ]

                     
                     hover = HoverTool(#names=hovernames,
                            mode="vline",                                        
                            tooltips = tooltips, 
                            formatters=formatters,
                            renderers = renderers #[ cp, np, ],
                     )
                     p.add_tools(hover)
                     p.add_layout(p.legend[0], 'right')                     

                     st.bokeh_chart(p, use_container_width=True)


                     q = figure(
                            x_axis_type="datetime", x_axis_location="below",
                            x_range=Range1d(df['time'][0], df['time'][-1]),
                            title='Jobs',
                            x_axis_label='Time',
                            y_axis_label='Jobs',
                            height=300,
                     )

                     hover2 = HoverTool(
                            tooltips =tooltips,
                            formatters= formatters, #{
                            mode="vline",         
                            )
                     hover2.renderers = []
                     colors = ['red', 'green', 'blue', 'orange']
                     for col in job_cols:                           
                           hr_render=  q.line( df['time'],df[col], 
                                   color = colors[job_cols.index(col)],
                                   legend_label=col)
                           hover2.renderers.append(hr_render)

                     q.add_tools(hover2)
                     q.add_layout(q.legend[0], 'right')                     

                     st.bokeh_chart(q, use_container_width=True)
                     
                     with st.expander('Data (' + str(len(df)) + ' items)' ):
                            st.dataframe(df)

              st.spinner("Done")
