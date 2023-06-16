try:
    import drmaa
except:
    print("DRMAA not available")
    drmaa_avail = False

import time
import os,sys


def submit_job(command, jobname, select, email):
    
  if not drmaa_avail:
    pbs_sub = drmaa.Session()
    pbs_sub.initialize()
    jt = pbs_sub.createJobTemplate()
    jt.remoteCommand = command
    jt.jobName = jobname 
    jt.nativeSpecification = select
    jt.joinFiles=False
    jt.email = email 

    jobid = pbs_sub.runJob(jt)
    print( 'Your job has been submitted with id ' + jobid )
    return jobid
    pbs_sub.deleteJobTemplate(jt)
    pbs_sub.exit()
  else:
    print("Sorry, DRMAA not available")




def check_job(jobid):

    decodestatus = {
        drmaa.JobState.UNDETERMINED: 'process status cannot be determined',
        drmaa.JobState.QUEUED_ACTIVE: 'job is queued and active',
        drmaa.JobState.SYSTEM_ON_HOLD: 'job is queued and in system hold',
        drmaa.JobState.USER_ON_HOLD: 'job is queued and in user hold',
        drmaa.JobState.USER_SYSTEM_ON_HOLD: 'job is queued and in user and system hold',
        drmaa.JobState.RUNNING: 'job is running',
        drmaa.JobState.SYSTEM_SUSPENDED: 'job is system suspended',
        drmaa.JobState.USER_SUSPENDED: 'job is user suspended',
        drmaa.JobState.DONE: 'job finished normally',
        drmaa.JobState.FAILED: 'job finished, but failed',
        }
    
#    if len(sys.argv) > 1:

    pbs = drmaa.Session()
    try:
      pbs.initialize()
    except:
      pass
    return (decodestatus[pbs.jobStatus(jobid)])
    pbs.exit()



def test():
    if len(sys.argv) > 1:
        check_job(sys.argv[1] )
    else:
        jobid=submit_job('/home/ischeepers/hello','Hello-Test', '-l select=1:ncpus=1 -q serial -l walltime=5:00 -P SCHPC', 'ischeepers@csir.co.za')
        time.sleep(5)
        check_job(jobid)


 
