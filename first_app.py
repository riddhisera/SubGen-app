import streamlit as st
import os
import base64
import pandas as pd

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    data = [(1, 2, 3)]
    # When no file name is given, pandas returns the CSV as a string, nice.
    df = pd.DataFrame(data, columns=["Col1", "Col2", "Col3"])
    csv = df.to_csv(index=False)

    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href



st.title('Drug Discovery using Subtractive Genomics Analysis')
"Find `drug targets` for your organism using `Subtractive Genomics Approch`"

st.header('Getting started:')
st.subheader('What is Subtractive Genomic Analysis?')
"It is an in-silico approach used to gradually reduce the whole proteome of pathogen to few potential and novel proteins that can act as drug targets."

st.subheader('What are the steps followed?')
st.markdown("""
- Collect whole proteome of target organism from NCBI 
- Perform clustering using CD-HIT to filter unique proteins
- Perform Local blast with Human & Mouse
- Perform Local blast with DEG database
- Perform Blast with know drug targets to identify novel and non-novel proteins
- Identify protein localization and structuralization
""")
st.subheader('How do I use this tool?')
"`STEP 1:` Collect the proteome data from the NCBI-protein database into a single fasta file."
st.info('If your target organism is Escherichia coli, go to https://www.ncbi.nlm.nih.gov/protein/?term=Escherichia+coli and download the Fasta file for all the results using the "Send to:" option')
"`STEP 2:` Perform clustering using CD-HIT"
st.info('Go to: http://weizhong-lab.ucsd.edu/cdhit_suite/cgi-bin/index.cgi?cmd=cd-hit and load the Fasta file from step one. Set the sequence identity cut-off to 0.8 and leave the rest of the parameters to default. Give your mail address and click Submit!')

# Sidebar
with st.sidebar.header('File splitter (for step 2)'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['Fasta'])
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    
if st.sidebar.button('Split'):
    # split the uploaded_file
    st.sidebar.info('Done! collect your files from below by right clicking the link & save as')
    st.sidebar.markdown(get_table_download_link(load_data), unsafe_allow_html=True)
else:
    st.sidebar.write("[Example input file](https://raw.githubusercontent.com/dataprofessor/bioactivity-prediction-app/main/example_acetylcholinesterase.txt)")
    st.sidebar.info('Upload input data in the sidebar to start!')

