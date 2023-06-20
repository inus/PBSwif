# status.py
import json
import os
import pandas as pd
import re
import streamlit as st
from subprocess import run
from pbs import DRMAA_avail

global saved_jobids
saved_jobids= []

def show_status(st, status_tab):        

    df_all = pd.DataFrame()

    def get_drmaa_jobstats():                
            try:
                jobs = run("qstat -xu $USER | awk '{ print $1 }' | tail -12 ",capture_output=True,shell=True)
            except:
                st.error('Cannot run qstat command on local host')
                return

            jobids = [x for x in jobs.stdout.splitlines()]
            jobids.reverse() 

            for jobid  in jobids:
                jobdetail  = run("qstat -xf -F json " + jobid.decode(), capture_output=True, shell=True)
                df = pd.read_json(jobdetail.stdout.decode() )
                ndf = pd.json_normalize(df.Jobs)
                ndf.insert(0, 'Job ID', jobid.decode())
                #ndf.insert(0, 'Exit', "OK" if ndf.iloc[0].Exit_status == 0 else "Fail")
                df_all = pd.concat([df_all, ndf])

            try:
                df_all.set_index('Job ID', inplace=True)
            except:
                pass

    '''
    def get_jobstats(jobid):
        
        filename='jobstats.json'
        if os.path.isfile(filename):          
            if os.path.getsize(filename) != 0:
                fp = open(filename)
                saved_jobstats = pd.read_json(filename)
                fp.close()
                print("DEBUG jobstats from file " + str(len(saved_jobstats)))
                return saved_jobstats
          
        else:
            return get_ssh_jobdetails(jobid)

    def get_ssh_jobdetails(jobid):

           #st.spinner("Completed")

        #print ("DEBUG : getting ssh job details: ") # + str(j))
        creds = st.session_state.user + '@' + st.session_state.server 
###        cmd = 'qstat -x -f -F json -w ' +  str(jobid) 
        cmd = 'qstat -x -f -F json -w  -u $USER ' +  str(jobid) 
        qstat = run("ssh " + creds + ' ' + cmd, capture_output=True, shell=True) 
        #print("DEBUG: after jobdetails: length of record ")# + \
        if qstat:
            lines = [x.decode() for x in qstat.stdout.splitlines()]
            data = [ l.split() for l in lines]                

        #print ("DEBUG : qstat stdout ", data)

        jsondata = json.loads(qstat.stdout.decode())
        jdf = pd.DataFrame(jsondata)
#        df = pd.DataFrame(jdf.Jobs)
        ndf = pd.json_normalize(jdf.Jobs )
        ndf.insert(0, 'Job ID', jobid)
        
        #print("DEBUG: jsondata ", ndf) 
        return pd.DataFrame(ndf)


    def save_jobstats_to_file(data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f)
            f.close()
            print("DEBUG: after write new jobstats json")
    '''
                

    def get_jobstats():
        with st.spinner("Getting job data..."):
              creds = st.session_state.user + '@' + st.session_state.server 
              cmd = 'qstat -x -F json -f -w -u' + st.session_state.user # <<< admin mode needs other usernames
              qstat = run("ssh " + creds + ' ' + cmd, capture_output=True, shell=True)      
              jdf = pd.read_json(qstat.stdout.decode())
              ndf = pd.json_normalize(jdf.Jobs)           # <<<<<<<<<<<<
              #ndf.insert(0, 'Job ID', 123)
              df = pd.DataFrame(ndf)        
        st.spinner("Completed")
        return df

    
    with status_tab:
        if DRMAA_avail:
            get_drmaa_jobstats()
        else:
            print("DEbug ",st.session_state.user )
            if st.session_state.user != "":
                job_df = get_jobstats()
                st.dataframe(job_df)

