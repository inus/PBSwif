# Status.py

import re,json
from subprocess import run
import pandas as pd

def show_status(st, status_tab):

  joblist = []
  df_all = pd.DataFrame()

  with status_tab:

    jobs = run("qstat -xu $USER | awk '{ print $1 }' | tail -12 ",capture_output=True,shell=True)
    jobids = [x for x in jobs.stdout.splitlines()]
    jobids.reverse() #  in jobs.stdout.splitlines():

    for jobid  in jobids:

        jobdetail  = run("qstat -xf -F json " + jobid.decode(), capture_output=True, shell=True)
        df = pd.read_json(jobdetail.stdout.decode() )
        ndf = pd.json_normalize(df.Jobs)
        df_all = pd.concat([df_all, ndf])

    st.dataframe(df_all)


