#setup_ssh.py

import os
import pexpect
import re
from subprocess import run
import streamlit as st

#COMMAND_PROMPT = '[$#] '
#TERMINAL_PROMPT = r'Terminal type\?'
#TERMINAL_TYPE = 'vt100'
SSH_NEWKEY = r'Are you sure you want to continue connecting \(yes/no\)\?'
'''
ssh-keygen -t ed25519 -C 'PBSwif' -P '' -f PBSwif.ed25519
ssh-copy-id  -i PBSwif.ed25519 ischeepers@scp.chpc.ac.za
ssh   -i PBSwif.ed25519  scp whoami
'''
def show_setup(st, setup):


    def login_with_pass():
        cmd = 'ssh  -o PubkeyAuthentication=no' + ' ' +  st.session_state.user + '@' + st.session_state.server + ' whoami'
        child = pexpect.spawn(cmd)

        i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, '[Pp]assword: '])
        if i == 0: # Timeout
            print('ERROR!')
            print('SSH could not login. Here is what SSH said:')
            #print(child.before, child.after)
            return False
            #sys.exit (1)
        if i == 1: # SSH does not have the public key. Just accept it.
            print('Prompt received')
            child.sendline ('yes')
            child.expect ('[Pp]assword: ')
        child.sendline(st.session_state.passw)
        # Now we are either at the command prompt or
        # the login process is asking for our terminal type.
#        i = child.expect (['Permission denied', TERMINAL_PROMPT, COMMAND_PROMPT])
        i = child.expect (['Permission denied', st.session_state.user,  pexpect.EOF ], )
        if i == 0:
            st.error('Permission denied for ' + st.session_state.user +'@' + st.session_state.server)            
            return False
            #sys.exit (1)
        if i == 1:
#            child.sendline (TERMINAL_TYPE)
            #child.expect (st.session_state.user)
            print('Received ', child.after.decode())
            return True
            #login_OK = True

        if i == 2:
            print('SSH received EOF')
            return False


        return False #child


###############################################################################

    passw = st.text_input("Password", value="", key='passw', type='password')
              #type="default", help=None, autocomplete=None, on_change=None, args=None, 
              #kwargs=None, *, placeholder=None, disabled=False, label_visibility="visible")
    if st.session_state.passw != "":

        if login_with_pass():

            st.success('Login success!')
            #file = 'PBSwif.ed25519'
            keyfile = os.environ['HOME'] +'/.ssh/' +  'PBSwif.ed25519'

            if not os.path.exists(keyfile):

                if st.button( 'Generate ssh key'):
                    print("DEBUG")
                    print('ssh-keygen -t ed25519 -P "" -f ' + keyfile + ' -C "PBSwif" ')

                    os.system('ssh-keygen -t ed25519 -P "" -f ' + keyfile + ' -C "PBSwif" ')
                    if os.path.exists(keyfile):            
                            st.success("Keyfile created")
                    else:
                            st.error('ssh-keygen failed') 
            else:
                st.info('Key file ' + keyfile + ' already exists' )

            if st.button( 'Copy key ' +  keyfile + ' to server'):
                    os.system("ssh-copy-id  -i " + keyfile  + ' ' +
                          st.session_state.user + '@' + st.session_state.server)

            if st.button( 'Test \"whoami" command via ssh with keyfile ' + keyfile):
                    try:
                        output = run("ssh -i " + keyfile + ' ' +
                          st.session_state.user + '@' + st.session_state.server + ' whoami', 
                                capture_output=True, shell=True, check=True, timeout=8)
                        st.text( output.stdout.decode())
                        st.text( output.stderr.decode())

                    except TimeoutError as t:
                         st.error("SSH failed with keyfile " + keyfile + ':' + str(t))

            if st.button( 'Completed ssh setup'):
                         return True

            

# if login_with_pass ok
#    generate key
#    copy id
#  test key         

    
