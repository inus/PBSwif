# status.py

import re,json
from subprocess import run
import pandas as pd

def show_status(st, status_tab):

  joblist = []
  df_all = pd.DataFrame()

  with status_tab:

    jobs = run("qstat -xu $USER | awk '{ print $1 }' | tail -12 ",capture_output=True,shell=True)
    jobids = [x for x in jobs.stdout.splitlines()]
    jobids.reverse() 

    for jobid  in jobids:

        jobdetail  = run("qstat -xf -F json " + jobid.decode(), capture_output=True, shell=True)
        df = pd.read_json(jobdetail.stdout.decode() )
        ndf = pd.json_normalize(df.Jobs)
        ndf.insert(0, 'Job ID', jobid.decode())
        ndf.insert(0, 'Exit', "OK" if ndf.iloc[0].Exit_status == 0 else "Fail")
        df_all = pd.concat([df_all, ndf])

    try:
      df_all.set_index('Job ID', inplace=True)
    except:
       pass
    st.dataframe(df_all)


