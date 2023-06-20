# status.py
import streamlit as st

import re,json
from subprocess import run
import pandas as pd
from pbs import DRMAA_avail

def show_status(st, status_tab):

  joblist = []
  df_all = pd.DataFrame()

  with status_tab:

        jobdetails = st.checkbox('Retrieve full job history', key='jobdetails')

        if DRMAA_avail:
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

        else:  #Use SSH
           if st.session_state.use_ssh and (st.session_state.user != "user"):
                creds = st.session_state.user + '@' + st.session_state.server 
                cmd = 'qstat -xu ' + st.session_state.user + " | awk '{ print $1 }' " 
                if st.session_state.user != "user":
                  print("DEBUG: before call qstat ssh")
                  #try:
                  jobs = run("ssh " + creds + ' ' + cmd, capture_output=True, shell=True) # check=True,timeout=15)                      
                  print("DEBUG: after call ssh x" + cmd )
#                  print(jobs)

                  idlist = jobs.stdout.decode()
                  print(idlist)


                  st.info("Found " + 'len(jobs)' + "completed jobs")
                  #except:
                  #    print("SSH qstat error ")
                  #    return 

                  lines = [x.decode() for x in jobs.stdout.splitlines() ]
                  print("DEBUG: lines ")
                  #print(lines)

                  jobids = [ x for x in lines if re.search("^\d+.sched01", x)]
                  if jobids: 
                    jobids.reverse() #latest on top
                    df_all = pd.DataFrame()
                    for j in jobids:

                        print("DEBUG: jobids ")
                        print(j)

                        cmd = 'qstat -xf -F json ' +  str(j) 

                        print("DEBUG: before jobdetails")
                        print(cmd)

                        if st.session_state.jobdetails:
                            full_job = run("ssh " + creds + ' ' + cmd, capture_output=True, shell=True) 
                                    
                            print("DEBUG: after jobdetails")
                            print(full_job.returncode)

                            df = pd.read_json(full_job.stdout.decode())
                            print("DEBUG: after read json")

                            ndf = pd.json_normalize(df.Jobs)
                            ndf.insert(0, 'Job ID', j)
                            df_all = pd.concat([df_all, ndf])

                    print("DEBUG: before index")

                    try:
                        df_all.set_index('Job ID', inplace=True)
                    except:
                        pass
                    print("DEBUG: after indexind")
                    
                  print("DEBUG: before df")
                  st.dataframe(df_all)
                  print("DEBUG: after df")
                  df_all 


            #except:
            #    st.error("SSH {} timed out for".format(creds))
            #    return                 
          #else:
          #   st.error("Invalid cluster user {} for Qstat".format(st.session_state.user))
              #return 
          #if jobs.returncode > 0:
