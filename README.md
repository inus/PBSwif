# Streamlit app to interact with CHPC Lengau Cluster:

- To aid in generating PBS job scripts using CHPC queue parameters

- To submit job scripts to the cluster from a web interface

- To track and display queue and job status on the cluster

- Extend capabilities to generate graphs from results


## To install:

- Check out git code directory `git clone https://github.com/inus/PBSwif.git`

- Create a python (tested on 3.9 and 3.11) virtual env, and activate

  `virtualenv Venv3`
  
  `. Venv3/bin/activate`

- Install streamlit and optionally drmaa, to enable job submission.

  `pip install streamlit`


  Note that the DRMAA v1 library has to be compiled or installed on the
  submit host.
  
  The library path can be provided via shell environment variable, `DRMAA_LIBRARY_PATH` 
  
  `pip install drmaa` 
  

## Run the app

- `streamlit run app.py`

- Open browser on localhost:8501

- Alternatively, when running on a remote/login node:
  
  open a ssh tunnel, eg:
   `ssh -N -L 10000:localhost:8501 scp.chpc.ac.za`

