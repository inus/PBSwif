#plot.py
import streamlit as st

import numpy as np

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool, Range1d, HoverTool, Circle
from bokeh.plotting import figure


def plot_bokeh(df):

    dates = np.array(df.time, dtype=np.datetime64)
    source = ColumnDataSource(df)

    tools = "pan, box_zoom, save, reset, help, xwheel_zoom, crosshair"

    p = figure(height=400, width=800, tools=tools, toolbar_location='below',            
            x_axis_type="datetime", x_axis_location="below",
            background_fill_color="#efefef", 
            x_range=Range1d(dates[0], dates[-1]),
            y_range=(0, int(max(df.jobs_running.max(), df.jobs_queued.max() )))
            )
    p.title.text = "Lengau Queue"
    p.title.align = "left"
    p.title.text_color = "black"
    p.title.text_font_size = "25px"
    
    hover_circle = Circle(x="x", y="y", size=10, fill_color="red")
    circle = Circle(x="x", y="y", size=10, fill_color="white")

    hover = HoverTool(
        tooltips = [
            ("Time", "@time{%F %H:%M}"),
            ("Running", "@jobs_running"),
            ("Queued", "@jobs_queued"),
        ],
        formatters={
            '@time'           : 'datetime', # use 'datetime' formatter for '@date' field
            '@{jobs_running}' : 'printf',   # use 'printf' formatter for '@{adj close}' field
            '@{jobs_queued}'  : 'printf',   # use default 'numeral' formatter for other fields
         },
         mode="vline",         
         )


    #circle_renderer = p.add_glyph(source, circle)
    #c = p.add_glyph('jobs_running', circle, hover_glyph=hover_circle)

    p.yaxis.axis_label = 'No. of Jobs'

    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                    height=100, width=800, y_range=p.y_range,
                    x_axis_type="datetime", y_axis_type=None,
                    tools="hover", 
                    toolbar_location=None, 
                    background_fill_color="#efefef")
    

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.75

    select.line('time', 'jobs_running', source=source)
    select.line('time', 'jobs_queued', source=source)
    select.ygrid.grid_line_color = 'black'
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool


    p.circle_x('time', 'jobs_running', color='green',
                source=source, alpha=1.0,
                legend_label="Running",) #.hover_glyph(hover)

    df12 = df.time[::12]
    jr12 = df.jobs_running[::12]
    p.circle_x(df12, jr12, color='lightgreen', 
                alpha=0.9,legend_label="Running",)

    #         selection_color='red', nonselection_alpha=0.5, size=30)
    #p.circle_y('time', 'jobs_running', source=source, color='lightgreen', alpha=0.5, size=20,legend_label="Held")
    #         legend_label="Running")
    #p.step('time', 'jobs_running', source=source, color='green', alpha=0.75, legend_label="Running")
    
    p.circle_x( 'time', 'jobs_queued', source=source, color='blue', alpha=0.5, legend_label="Queued")
    #p.step( 'time', 'jobs_queued', source=source, color='blue', alpha=0.5, legend_label="Queued")

    p.circle_x( 'time', 'jobs_exiting', source=source, color='red', alpha=0.5, legend_label="Held", size=10)

    p.circle_x( 'time', 'jobs_held', source=source, color='black', alpha=0.5, legend_label="Exiting", size=10)


    #p.add_tools(hover)


    f = column(p,select) 
    st.bokeh_chart(f, use_container_width=True)

