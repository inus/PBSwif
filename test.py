#test.py 

import re,json
from subprocess import run
import pandas as pd

def show_test(st, test_tab):

  joblist = []
#  df_all = pd.DataFrame()

  with test_tab:

#    if st.session_state.use_ssh:
    with st.form(key='test_form'):

        if st.form_submit_button('Test SSH', use_container_width=True, type="primary"):

            if st.session_state.use_ssh:
                creds = st.session_state.user + '@' + st.session_state.server 
                cmd = 'qstat -xu ' + st.session_state.user + " | awk '{ print $1 }' " 

                try:
                    jobs = run("ssh " + creds + ' ' + cmd, capture_output=True, shell=True)
                except:
                    st.error("SSH {} failed ".format(creds))
                    return 

                lines = [x.decode() for x in jobs.stdout.splitlines() ]
                jobids = [ x for x in lines if re.search("^\d+.sched01", x)]
                if jobids: 
                    fulljobs = []
                    df_all = pd.DataFrame()
                    for j in jobids:
                        cmd = 'qstat -xf -F json ' +  str(j) 
                        jobdetails = run("ssh " + creds + ' ' + cmd, capture_output=True, shell=True)

                        df = pd.read_json(jobdetails.stdout.decode())

                        ndf = pd.json_normalize(df.Jobs)
                        ndf.insert(0, 'Job ID', j)


                        #fulljobs.append(jobdetails)
                        #ndf.insert(0, 'Exit', "OK" if ndf.iloc[0].Exit_status == 0 else "Fail")
                        #st.table(ndf)

                        df_all = pd.concat([df_all, ndf])
                        #import pdb; pdb.set_trace()


                    try:
                        df_all.set_index('Job ID', inplace=True)
                    except:
                        pass
                    
                    st.dataframe(df_all)

#                    st.table(df_all)  

                    '''
                    #df = pd.read_json(''.join(fulljobs))
                    ndf = pd.json_normalize(df.Jobs)
                    ndf.insert(0, 'Job ID', jobid.decode())
                    ndf.insert(0, 'Exit', "OK" if ndf.iloc[0].Exit_status == 0 else "Fail")
                    df_all = pd.concat([df_all, ndf])

                    '''
                   
                else:
                   write(":(")

            else:
               st.warning("SSH is disabled")

