import streamlit as st
import os
import base64
import pandas as pd
import io

##################### FUNCTIONS #####################

def download_link(object_to_download, download_filename, download_link_text):   # Generates a link to download the given object_to_download.
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def splitter(input_file, no_seq=500):   # to split files into 50MB    
    mylist = input_file.split(">")[1:]
    n = len(mylist)//no_seq + 2
    x = 0
    s = ''

    newlist = []
    for i in range(1,n):
        for text in mylist[x:(i)*no_seq]:
            s += ">"+text
        x = i*no_seq 
        newlist.append(s)
        s = ''
    return newlist

def combiner(input_files): # to combine files for blast
    output = ''
    for file in input_files:
        stringio = io.StringIO(file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        output += string_data + '\n'
    return output

##################### MAIN TEXT ###################################

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
st.info('Go to: http://weizhong-lab.ucsd.edu/cdhit_suite/cgi-bin/index.cgi?cmd=cd-hit and load the Fasta file from step one. Set the sequence identity cut-off to 0.8 and leave the rest of the parameters to its default values. Give your mail address and click Submit!')
"`STEP 3:` Perform Local blast with Human & Mouse protein data"
st.info('Click here to get the combined Human & Mouse data you need to perform blast [insert link]. Perform local blast on your computer.')


######################### Sidebar ######################

st.sidebar.title('Tools to help you!')

with st.sidebar.header('File splitter (for step 2)'):
    uploaded_file = st.sidebar.file_uploader("To split files into smaller pieces of 50MB as required by the CD-HIT suite", type=['Fasta','txt'])

int_val = st.sidebar.number_input('Specify how many sequences you want in a file, the default is set to 500', min_value=1, max_value=1000, value=500, step=100)

if st.sidebar.button('Split'):
    stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()

    for s, i in zip(splitter(string_data, int_val),range(1,int_val+1)):
        tmp_download_link = download_link(s, 'file'+str(i)+'.txt', 'download file '+str(i))
        st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)
else:
    st.sidebar.write('`Upload input data in the sidebar to get started!`')


with st.sidebar.header('File combiner (for step 3)'):
    uploaded_files = st.sidebar.file_uploader("To combine the split files from CD HIT to perform Blast", type=['Fasta','txt'], accept_multiple_files=True)

if st.sidebar.button('Combine'):
    tmp_download_link = download_link(combiner(uploaded_files), 'combinedfile.txt', 'download combined file')
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)
else:
    st.sidebar.write('`Upload input data in the sidebar to get started!`')

