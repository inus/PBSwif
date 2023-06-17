import re,json
from subprocess import run

def show_status(st, status_tab):

  joblist = []
  with status_tab:
    jobs = run("qstat -xu $USER | awk '{ print $1 }' | tail -12 ",capture_output=True,shell=True)
    jobids = [x for x in jobs.stdout.splitlines()]
    jobids.reverse() #  in jobs.stdout.splitlines():
    for jobid  in jobids:
        jobdetail  = run("qstat -xf -F json " + jobid.decode(), capture_output=True, shell=True)
        joblist.append(jobdetail.stdout)

        X = jobid.decode() #+ re.sub('comment = Job run at ', '', jobdetail.stdout.decode())

        jobdict = json.loads(jobdetail.stdout)
        st.write(str(jobid.decode()), '\t',
                jobdict['Jobs'][X]['Job_Name'], '\t',
                jobdict['Jobs'][X]['job_state'], '\t',
                str(jobdict['Jobs'][X]['resources_used']['cpupercent']), '\t',
                str(jobdict['Jobs'][X]['resources_used']['ncpus']), '\t',
                str(jobdict['Jobs'][X]['resources_used']['cput']), '\t',
                str(jobdict['Jobs'][X]['resources_used']['mem']), '\t',
                str(jobdict['Jobs'][X]['Exit_status']), '\t',
                (jobdict['Jobs'][X]['etime']),
                )


