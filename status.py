import re
from subprocess import run
#from common import configuration
from pbs_drmaa_status import check_job

def show_status(st, status_tab):

  with status_tab:
    jobs = run("qstat -xu $USER | awk '{ print $1 }' | tail -12 ",capture_output=True,shell=True)
    for jobid  in jobs.stdout.splitlines():
        jobdetail  = run("qstat -xf " + jobid.decode() + " | grep comment" ,capture_output=True,shell=True)
        X = jobid.decode() + re.sub('comment = Job run at ', '', jobdetail.stdout.decode())
        st.text(X)

#        failed =  re.match('fail', X)
#        if  re.search('fail',X):
#                st.write(':red[' + X + ']')
#        else:   
#                st.write(':green[' + X + ']')
#

        


