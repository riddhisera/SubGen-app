import streamlit as st
import base64
import pandas as pd
import io
import os, glob
##################### FUNCTIONS #####################

def download_link(object_to_download, download_filename, download_link_text):   # Generates a link to download the given object_to_download.

    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
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

def nohitsfile(cd,blast,hits,nohits): #this code creates 2 text files with queries of those that gave hits and those that didnt 
    stringio = io.StringIO(cd.getvalue().decode("utf-8"))
    cd = stringio.read()
    stringio = io.StringIO(blast.getvalue().decode("utf-8"))
    blast = stringio.read()

    blastlist = blast.splitlines() 
    cdlist = cd.split(">") 
    hitsdata = []
    nohitsdata = []
    hitstext = ''
    nohitstext = ''
    output1 = ''
    output2 = ''

    for line,x in zip(blastlist,range(len(blastlist))):
        if "Query=" in line:
            if "***** No hits found *****" in blastlist[x+5:x+10]:
                nohitsdata.append(blastlist[x])
                nohitstext += blastlist[x] + "\n"
            else:
                hitsdata.append(blastlist[x])
                hitstext += blastlist[x] + "\n"
    
    st.sidebar.write("number of no hits sequences = ",len(nohitsdata))
    st.sidebar.write("number of hits sequences = ",len(hitsdata))

    for line in cdlist:
        if line[0:20] in nohitstext:
            output1 += ">" + line + '\n'
        else:
            output2 += ">" + line + '\n'

    output1 = output1[1:]

    if hits is True and nohits is False:
        st.sidebar.write("number of sequences in your result file= ",output2.count('>'))
        return output2
    elif nohits is True and hits is False:
        st.sidebar.write("number of sequences in your result file= ",output1.count('>'))
        return output1

def combcsv(input_files):
    df_from_each_file = (pd.read_csv(f, sep=',') for f in input_files)
    df_merged   = pd.concat(df_from_each_file, ignore_index=True)
    return df_merged
    
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
- Perform Blast with known drug targets to identify novel and non-novel proteins
- Identify protein localization and structuralization
""")
st.subheader('How do I use this tool?')
"`STEP 1:` Collect the proteome data from the NCBI-protein database into a single fasta file."
st.info('If your target organism is Escherichia coli, go to https://www.ncbi.nlm.nih.gov/protein/?term=Escherichia+coli and download the Fasta file for all the results using the "Send to:" option')
"`STEP 2:` Perform clustering using CD-HIT"
st.info('Go to: http://weizhong-lab.ucsd.edu/cdhit_suite/cgi-bin/index.cgi?cmd=cd-hit and load the Fasta file from step one. Set the sequence identity cut-off to 0.8 and leave the rest of the parameters to its default values. Give your mail address and click Submit!')
"`STEP 3:` Perform Local blast with Human & Mouse protein data"
st.info('Click here to get the combined Human & Mouse data you need to perform blast [insert link]. Perform local blast on your computer. Using the results file, you can use the tool in the sidebar to get the sequences with no hits.')
"`STEP 4:` Perform Local blast with DEG database"
st.info('Click here to get the combined DEG data you need to perform blast [insert link]. Perform local blast on your computer. Using the results file, you can use the tool in the sidebar to get the sequences with hits.')
"`STEP 5:` Identify novel and non-novel sequences"
st.info('Asses the resulting proteins through BLASTp against FDA approved protein drug targets from DrugBank [link to data]. Using the results file, you can use the tool in the sidebar to get the sequences with hits or no hits.')
"`STEP 6:` Local and functional analysis of the prospective sequences"
st.info('You can use tools like KEGG (https://www.genome.jp/kegg/) to analyze the metabolic pathways, BUSCA (http://busca.biocomp.unibo.it/) for predicting protein subcellular localization and eggNOG-mapper (http://eggnog-mapper.embl.de/) for the functional annotation of large sets of sequences.')

"`FINAL:` Using the shortlisted potential drugs from above, you can perform a structure based analysis for further developmental stages."

######################### Sidebar ######################

st.sidebar.title('Tools to help you!')

#FILE SPLITTER
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

#FILE COMBINER
with st.sidebar.header('File combiner (for step 3)'):
    uploaded_files = st.sidebar.file_uploader("To combine the split files from CD HIT to perform Blast", type=['Fasta','txt'], accept_multiple_files=True)

if st.sidebar.button('Combine'):
    tmp_download_link = download_link(combiner(uploaded_files), 'combinedfile.txt', 'download combined file')
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)
else:
    st.sidebar.write('`Upload input data in the sidebar to get started!`')

#HITS / NO HITS IDENTIFIER
with st.sidebar.header('Hits/No Hits identifier (for steps 3 and 4)'):
    cdfile = st.sidebar.file_uploader("Drop your QUERY file here", type=['Fasta','txt'])
    blastresultfile = st.sidebar.file_uploader("Drop your BLAST RESULT file here", type=['Fasta','txt'])

st.sidebar.subheader("Choose which file you need")    
hits, nohits = False, False
if st.sidebar.checkbox("With HITS"):
    hits = True
if st.sidebar.checkbox("Without HITS"):
    nohits = True
    
if st.sidebar.button('Result'):
    if (nohits is True and hits is True) or (nohits is False and hits is False):
        st.sidebar.write('OOPS! try choosing only one option')
    else:
        tmp_download_link = download_link(nohitsfile(cdfile,blastresultfile,hits,nohits), 'resut.txt', 'download your result file')
        st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)
else:
    st.sidebar.write('`Upload input data in the sidebar to get started!`')

st.sidebar.title('Extra tools!')

#OTHER TOOLS

#CSV FILE COMBINER
with st.sidebar.header('Combine your BUSCA results (csv) files here (for step 6)'):
    csvfiles = st.sidebar.file_uploader("To combine the split csv files from BUSCA into one single csv file", type=['csv'], accept_multiple_files=True)

if st.sidebar.button('Combine csv'):
    tmp_download_link = download_link(combcsv(csvfiles), 'combinedfile.csv', 'download combined file')
    st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)
else:
    st.sidebar.write('`Upload input data in the sidebar to get started!`')
