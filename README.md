Streamlit app to interact with CHPC Lengau Cluster:

1. To aid in generating PBS job scripts

2. To submit jobs from the web interface

3. To track queue and job status on the cluster


To install:

Check out git code directory

Create a python 3.11 virtual env, and activate

Install streamlit:

pip install -r requirements.txt

Run the app

streamlit run test.py

Open browser on localhost:8501

Alt. when running on a remote/login node:
open a ssh tunnel, eg:

ssh -N -L 10000:localhost:8501 scp.chpc.ac.za


