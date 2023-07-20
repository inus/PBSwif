#common.py
import socket
import streamlit as st

from sidebar import DEFAULT_WALLTIME
from qtable import table_md

copy_button='<div><style> button {-webkit-text-size-adjust: 100%; tab-size: 4;\
        --tw-text-opacity: 0.7;list-style-type: decimal;box-sizing: border-box;border-radius: 5px;\
        border: 1px solid grey;font-size: 100%;margin: 0;padding: 0;-webkit-appearance: button;\
        background-color: initial;position: relative;top: 0rem;right: 0rem;\
        margin-left:auto;display: flex;height: 3rem;width: 3rem;cursor: pointer;\
        align-items: center;}</style><button halign="right" class="button" type="button"\
                        data-copy-state="copy"><span>&#128203;Copy</span></button></div>'            
#    st.markdown(href, unsafe_allow_html=True)


def show_info():
  with st.expander("Show/hide CHPC Lengau PBS queue rules", expanded=False):
    st.markdown(table_md)

def show_email_options():
    print("Callback ")
    if  'Notify' in st.session_state:
        st.session_state.Notify = not st.session_state.Notify

def check_select(): 

    k = ['nodect', 'ncpus', 'mem', 'mpiprocs', 'ngpus', 'walltime']
    res = {}
    for s in k:
        res[s] = st.session_state[s]

    #Nodes, Cores, Memory, Queue, MPIprocs, GPUs, walltime = st.session_state.nodect, \
    #    st.session_state.ncpus, st.session_state.mem, st.session_state.Queue, \
    #    st.session_state.mpiprocs, st.session_state.ngpus, st.session_state.walltime

    res['walltime'] = int(res['walltime'][:2])

    if res['nodect'] == 1:
        if res['ngpus'] > 0:
            res['queue'] = 'gpu_' + str(res['ngpus'])
        else:
            if res['mem'] > 120:
                res['queue'] = 'bigmem'
                if res['walltime'] > 48: res['walltime'] = 48
            else:
                if res['ncpus'] == 24:
                    res['queue'] = 'smp'
                    if res['walltime'] > 96: res['walltime'] = 96
                else:
                    if res['walltime'] > 96: 
                        res['queue'] = 'seriallong'
                        if res['walltime'] > 144: res['walltime'] = 144
                    else:
                        res['queue'] = 'serial'
                        if res['walltime'] > 48: res['walltime'] = 48


    elif res['nodect'] >= 2:
        if res['ncpus'] < 24: 
            res['ncpus'] = 24
        res['queue'] = 'normal'
        if res['walltime'] > 48: res['walltime'] = 48

    elif res['nodect'] > 20:     # TODO: Check res['queue'] limits with Qstat            
        res['queue'] = 'large'
        if res['walltime'] > 96: res['walltime'] = 96

    else:
        res['queue'] = 'normal'
        if res['walltime'] > 48: res['walltime'] = 48

    if res['ngpus'] > 0:
        if res['ngpus'] == 1 : 
            if res['ncpus'] > 10: res['ncpus'] = 10
        if res['ngpus'] == 2 : 
            if res['ncpus'] > 20: res['ncpus'] = 20
        if res['ngpus'] == 3 : 
            if res['ncpus'] > 36: res['ncpus'] = 36
        if res['ngpus'] == 4 : 
            if res['ncpus'] > 40: res['ncpus'] = 40
        if res['walltime'] > 12:
            res['walltime'] = 12

    if res['mpiprocs'] > res['ncpus']:
            res['mpiprocs'] = res['ncpus']

        #select = "-l select={}:ncpus={}:nres['ngpus']={}:mpiprocs={}:mem={}GB".format(Nodes,res['ncpus'],GPUs,MPIprocs,res['mem'])

    #else:  #no GPU      
    #    if MPIprocs != 0:
    #        if MPIprocs > res['ncpus']: MPIprocs = Cores            
    #        select = "-l select={}:ncpus={}:mpiprocs={}:mem={}GB".format(Nodes,Cores,MPIprocs,res['mem'])
    #    else:
    #        select = "-l select={}:ncpus={}:mem={}GB".format(Nodes,Cores,res['mem'])
    
    #if st.session_state.place != "none":
    #    select = select + " -l place={}".format(st.session_state.place)

    #if st.session_state.walltime != DEFAULT_WALLTIME:
    #    select = select + " -l walltime=" + str(st.session_state.walltime) + ':' + str(st.session_state.walltime_m) 


    #st.session_state.nodect, st.session_state.ncpus, st.session_state.mem, st.session_state.Queue, \
    #    st.session_state.mpiprocs, st.session_state.ngpus, st.session_state.walltime = \
    #        Nodes, Cores, res['mem'], Queue, MPIprocs, GPUs, walltime 

    #return select, Nodes, Cores, res['mem'], Queue, MPIprocs, GPUs, walltime 
    return res 


def save_settings():
    fp = open('settings.conf', 'w')
    fp.write('sshuser=' + st.session_state.sshuser)
    fp.write('programme=' + st.session_state.programme)
    fp.close()

def read_settings():
    fp = open('settings.conf',)
#    fp.read('sshuser=' + st.session_state.sshuser)
#    fp.write('programme=' + st.session_state.programme)
#    fp.close()
