# jobs.py
import json
import pandas as pd
import polars as pl 
import re
import streamlit as st
from subprocess import run, TimeoutExpired, CalledProcessError, CompletedProcess
import inet
from pbs import DRMAA_avail

SSH_TIMEOUT=15

class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)



def show_jobs(st, status_tab):  

    def  get_user():
        if st.session_state.admin:
            if st.session_state.target_user != "":
                return st.session_state.target_user             
        else:
            return st.session_state.user
        
    def get_jobstats():

        def  get_ssh_jobs(creds, CMD):
            try:
                user = get_user()
                if user==None: 
                     cmd = creds + CMD
                else:
                     cmd = creds + CMD + '-u ' + user
                try:
                    jobs = run("ssh " + cmd,
                                capture_output=True, shell=True,
                                timeout=SSH_TIMEOUT, check=True)                     
                except CalledProcessError as c:
                    st.error('Could not run SSH command, error' + str(c))
                    return pd.DataFrame({'Jobs': [0]}) 
            except TimeoutExpired as t:
                    st.error("Check username, ssh " + creds + " failed: " + str(t))
                    return pd.DataFrame({'Jobs': [0]}) 

            return jobs


        def filter_qstat_json(jobs):
                dd = jobs.stdout.decode()
                dd=re.sub('\"COMP_WORDBREAKS\".*+\n', '', dd)
                dd=re.sub('\"CONDA_PROMPT_MODIFIER\".*+\n', '', dd)
                dd=re.sub('\\\\','',dd)
                dd=re.sub('\"\$\@\"','',dd)
                dd=re.sub(':nan',':\"nan\"',dd)

                try:
                    df =  json.loads(dd)
                except Exception as e:
                    print("Error in json.loads at ", e, '>>', '<<') # line )
                    print("dd[e.position]", '>>', dd[e.pos],  '<<') # line )
                    print("Chars: 10 before & after ", '>>', dd[e.pos-10:e.pos+15],  '<<') # line )
                    st.error('Can not read qstat json output: '  +  '>>' + dd[e.pos] + '<< ... '  +  dd[e.pos-8:e.pos+12] )
                    return dd
                return df



        def get_drmaa_jobs(creds, CMD):                
                
                if st.session_state.admin:
                    if st.session_state.target_user != "":
                        userarg  =  ' -u ' + st.session_state.target_user 
                    else:
                        userarg = ''
                else:
                        userarg = ' -u ' + st.session_state.user
                try:
                    jobs = run(CMD + userarg, capture_output=True, shell=True)
                except TimeoutError as t:
                    st.error("Qstat jobs via drmaa failed: " + str(t))
                    return pd.DataFrame({'Jobs' : []})            

#                dd = jobs.stdout.decode()
#                dd = filter_qstat_json(dd)
                df = filter_qstat_json(jobs)

#                dd=re.sub('\"COMP_WORDBREAKS\".*+\n', '', dd)
#                dd=re.sub('\"CONDA_PROMPT_MODIFIER\".*+\n', '', dd)
#                dd=re.sub('\\\\','',dd)
#                dd=re.sub('\"\$\@\"','',dd)
#
#                try:
#                    df =  json.loads(dd)
#                except Exception as e:
#                    import pdb; pdb.set_trace()
#                    print("Error in json.loads at ", e, '>>', '<<') # line )
#                    print("dd[e.position]", '>>', dd[e.pos],  '<<') # line )
#                    print("Chars: 10 before & after ", '>>', dd[e.pos-10:e.pos+15],  '<<') # line )
                    #st.error('Can not read qstat json output: '  +  '>>' + dd[e.pos] + '<< ... '  +  dd[e.pos-8:e.pos+12] )
#                    st.error('Can not read qstat json output: '  +  '>>' + str(e) + '<<')
#                    return

                if 'Jobs' in df.keys():
                        return pd.DataFrame(df)
                else:
                    return pd.DataFrame({'Jobs' : []})            



        #if  get_user() == None: #"" and 
        msg =  "Getting job data for "
        if st.session_state.admin:
            if st.session_state.target_user:                 
                msg +=  st.session_state.target_user 
            else:
                 msg += 'all users'
        else:
             msg += st.session_state.user


        with st.spinner(msg):
            creds = st.session_state.user 
            if not DRMAA_avail:
                    creds += '@' + st.session_state.server             

            CMD = ' qstat -f -w -F json -x ' 
             
            if DRMAA_avail:
                qstat = get_drmaa_jobs(creds,CMD) 
                return  qstat

            else:
                if st.session_state.user != "" and not re.search ( '\s', st.session_state.user): 
                    qstat = get_ssh_jobs(creds, CMD)    

            #if 'returncode' in qstat.keys(): 
            if type(qstat)==CompletedProcess:
                if qstat.returncode == 0:
                    #dd  = qstat.stdout.decode()
                    df = filter_qstat_json(qstat)

#                    dd=re.sub('\"COMP_WORDBREAKS\".*+\n', '', dd)
#                    dd=re.sub('\"CONDA_PROMPT_MODIFIER\".*+\n', '', dd)
#                    dd=re.sub('\\\\','',dd)
#                    dd=re.sub('\"\$\@\"','',dd)
#                    dd=re.sub(':nan',':\"nan\"',dd)
#
#                    try:
#                        df=json.loads(dd)
#                    except Exception as e:
#                        idx = int(str(e).split(' ')[-1].replace(')', ''))                   
#                        print("Error in json.loads at ", e, dd[idx-20:idx+20])
#                        import pdb; pdb.set_trace()
#                        st.error("Error in json.loads at :"  + dd[idx] + ': ' )
                        
                    if ( 'df' in locals() or 'df' in globals() ):
                        if 'Jobs' in df.keys():
                          return pd.DataFrame(df) 
                    df={}
                    return pd.DataFrame(df)
            else:
                st.error("Error reading job stats")
                return pd.DataFrame()

        st.spinner("Completed")            

        
    with status_tab:
        if inet.up():
            if st.session_state.user != "":
                df = get_jobstats()
            else:
                st.warning("Empty ssh username")
                return

            #import pdb; pdb.set_trace()
            if df is not None:
              if 'Jobs' in df.keys():    
                if len(df['Jobs'])!=0:
                    if get_user() == None: 
                            st.subheader('Showing ' + str(len(df['Jobs'])) + ' jobs for all users')       
                    else:
                            st.subheader('Showing ' + str(len(df['Jobs'])) + ' jobs for ' + get_user())
                    
                    #Xdf = pd.DataFrame(df['Jobs']) #[["Job_Name", "queue", "Job_Owner", "etime", "comment"]]
                    #Ydf = Xdf[["Job_Name", "queue", "Job_Owner", "etime", "comment"]]

                    #Tdf=pd.DataFrame(df['Jobs'], index=df.index)
                    #Zdf=pd.DataFrame(pd.json_normalize(df['Jobs']))
                    Zdf=pd.DataFrame.from_records(df.Jobs, index=df.index)
                    Xdf=pd.DataFrame( Zdf, index=df.index,
                            columns=['Job_Name', "queue", "Job_Owner", "project",
                                     'job_state', "stime", "mtime", "Exit_status", 
                                     "Submit_arguments",
                                     "Resource_List",
                                     'resources_used', 
                                     "comment",  
                                     'Error_Path', 'Output_Path'])
                    
                    cm_str = '.cm.cluster' #Zdf.iloc[0].Job_Owner
                    #host_str =  re.sub('^.*\@','@',full_str)
                    #re.sub('\@.*','',x)
                    Xdf.replace(to_replace=r'^.*\.cm\.cluster\:',value='', inplace=True, regex=True)

                    Xdf.replace(to_replace=r'\@.*\.cm.*$',value='', inplace=True, regex=True)

                    as_list=Xdf.index.tolist()
                    b_list = [re.sub('.sched01', '', x ) for x in as_list]
                    Xdf.index=b_list

                    st.data_editor(Xdf, column_config={ 
                        "_index" : "Job ID",
                        "resources_used" : st.column_config.ListColumn("Resources used"),
                        "Resource_List" : st.column_config.ListColumn("Resources req"),
                        #"rating": st.column_config.NumberColumn(),
                        "job_state": 'Job State',
                        "Job_Name" : 'Job name', 
                        "Job_Owner": 'Owner UID',
                        "stime" : "Start", #st.column_config.DatetimeColumn("Start time", format='HH:mm:ss YYYY-MM-DD') ,
                        "mtime" : "End", #st.column_config.DatetimeColumn("End time", format='HH:mm:ss YYYY-MM-DD') ,
                        "comment": "Comment",
                        "Exit_status": "Exit status",
                        "project" : "Project",
                        "Submit_arguments" : 'PBS script'
                        },
                        disabled=True)
                    

                else:
                     st.write('No jobs found') 

              else:
                    if st.session_state.target_user:
                       st.info("No recent PBS jobs for user **" + st.session_state.target_user + "**")
                    else:
                        st.info("No recent PBS jobs for user **" + st.session_state.user + "**")
        else:
            st.warning("No network connection")

