from requests.sessions import DEFAULT_REDIRECT_LIMIT
import streamlit as st
from pathlib import Path
import requests
import pandas as pd
import numpy as np
import altair as alt
from pandas.io.json import json_normalize
import base64
import SessionState

# sets up function to call Markdown File for "about"
def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


#main heading of the resource

st.header("CRIM Project Meta Data Viewer")

#st.subheader("These tools assemble metadata for about 5000 observations in Citations: The Renaissance Imitation Mass")
#st.write("Visit the [CRIM Project](https://crimproject.org) and its [Members Pages] (https://sites.google.com/haverford.edu/crim-project/home)")
#st.write("Also see the [Relationship Metadata Viewer] (https://crim-relationship-data-viewer.herokuapp.com/)")

# st.cache speeds things up by holding data in cache

@st.cache(allow_output_mutation=True)

# get the data function 
def get_data(link):
    data = requests.get(link).json()
    #df = pd.DataFrame(data)
    df = pd.json_normalize(data)
    return df 

#df = get_data('http://127.0.0.1:8000/data/observations/')
#df_r = get_data('http://127.0.0.1:8000/data/relationships/')

df = get_data('http://crimproject.org/data/observations/')
df_r = get_data('http://crimproject.org/data/relationships/')

#select_data = df[["id", "observer", "musical_type"]]
#select_data_r = df_r[["id", "observer", "relationship_type"]]

ema_test_data = df[["id", "piece.url", "ema", "piece.piece_id"]]
select_data = df[["id", "observer.name", "piece.piece_id", "musical_type"]]

select_data_r = df_r[['id', 'observer.name', 'model_observation.piece.piece_id', 'derivative_observation.piece.piece_id', 'relationship_type']]

# Sidebar options for _all_ data of a particular type

st.sidebar.write('Use checkboxes below to see all data of a given category.  Advanced filtering can be performed in the main window.')

if st.sidebar.checkbox('Show All Metadata Fields'):
    st.subheader('All CRIM Observations with All Metadata')
    st.write(df)

if st.sidebar.checkbox('Show Selected Metadata:  Observer, Type'):
    st.subheader('Selected Metadata:  Observer, Type')
    st.write(select_data)

if st.sidebar.checkbox('Show Total Observations per Analyst'):
    st.subheader('Total Observations per Analyst')
    st.write(df['observer'].value_counts())  


if st.sidebar.checkbox('Show Total Observations per Musical Type'):
    st.subheader('Total Observations per Musical Type')
    st.write(df['musical_type'].value_counts())
  

st.subheader("All Data and MEI Views")
sa = st.text_input('Name of file for download (must include ".csv")')
## Button to download CSV of results 
if st.button('Download Complete Dataset as CSV'):
    #s = st.text_input('Enter text here')
    tmp_download_link = download_link(df, sa, 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)



# These are the filters in the main window 
#st.header("Filter Views")
#st.write('Use the following dialogues to filter for one or more Observer, Piece, Observation, or Musical Type')
#st.write('To download a CSV file with the given results, provide a filename as requested, then click the download button')


#st.subheader("Select Observations by Observer")

#s1 = st.text_input('Name of Observer file for download (must include ".csv")')
# Button to download CSV of results 
#if st.button('Download Observer Results as CSV'):
#    #s = st.text_input('Enter text here')
#    tmp_download_link = download_link(select_data_1, s1, 'Click here to download your data!')
#    st.markdown(tmp_download_link, unsafe_allow_html=True)



#st.markdown("---")

def filter_by(filterer, select_data, full_data, key):
    options = select_data[filterer].unique().tolist()
    selected_options = st.multiselect('', options, key = key)
    list_of_selected = list(selected_options)

    if list_of_selected:
        chosen_columns =  select_data[filterer].isin(selected_options)
        subframe = select_data[chosen_columns]
        fullframe = full_data[chosen_columns]
    else:
        subframe = select_data
        fullframe = full_data
    
    return [fullframe, subframe]

st.markdown("---")
st.header("OBSERVATION VIEWER")

order = st.radio("Select order to filter data: ", ('Piece then Musical Type', 'Musical Type then Piece'))
if (order == 'Piece then Musical Type'):
    #filter by piece
    st.subheader("Piece")
    piece_frames = filter_by("piece.piece_id", select_data, df, 'a')
    piece_full = piece_frames[0]
    piece_sub = piece_frames[1]
    #st.write(piece_full)
    #st.write(piece_sub)

    #filter by type with or without piece
    st.subheader("Musical Type")
    mt_frames = filter_by('musical_type', piece_sub, piece_full, 'b')
    mt_full = mt_frames[0]
    mt_sub = mt_frames[1]
    st.markdown('Resulting observations:')
    #st.write(mt_full)
    st.write(mt_sub)
else:
    #filter by musical type
    st.subheader("Musical Type")
    mt_frames = filter_by('musical_type', select_data, df, 'z')
    mt_full = mt_frames[0]
    mt_sub = mt_frames[1]
    #st.write(mt_full)

    #filter by piece with or without musical type
    st.subheader("Piece")
    piece_frames = filter_by('piece.piece_id', mt_sub, mt_full, 'y')
    piece_full = piece_frames[0]
    piece_sub = piece_frames[1]
    st.markdown('Resulting observations:')
    st.write(piece_sub)



#List out all subfields for debugging
#col_list = [col for col in mt_full.columns if 'details.' in col ]
#st.write(col_list)

#Test subfield filters
#i = 0
#for col in col_list:
#    i=i+1
#    subfield_data = [True, False]
#    details_selected = st.radio('Choose ' + str(col), subfield_data, key=str(i))


    
#SessionState to filter musical types
#st.subheader("Musical Type 2")
#st.markdown("Using SessionState (?)")


#st.subheader('Example use of SessionState')
#def show_details(mtype):
#	if mtype == "Fuga":
#		list1 = ['Flexed','Inverted','Strict','Periodic']
#	elif mtype == "PEN":
#		list1 = ['Invertible','Strict','Flexed','Added','Sequential']
	
#	return list1

#def inp_det(type):
#    if type == 'musical type':
#        st.write('Enter name (Fuga/PEN)')
#        mtype = st.text_input('musical type name')
#    elif type == 'observer':
#        st.write('Enter name (Alice/Bob)')
#        mtype = st.text_input('observer name')
#    return mtype
    
#def main():
#    mtype = inp_det('musical type')
#    session_state = SessionState.get(name="", button_sent=False)
#    button_sent = st.button("SUBMIT")
#    if button_sent or session_state.button_sent: # <-- first time is button interaction, next time use state to go to multiselect
#        session_state.button_sent = True
#        listdetails = show_details(mtype)
#        selected=st.multiselect('Select the details',listdetails)
#        st.write(selected)

#if __name__ == "__main__":
#    main()


#Forms to have all information sent at the same time
#st.subheader("Musical Type 3")
#st.markdown("Using st.forms (?)")

#st.markdown("---")
#st.header("Replicate Site Search Views - Search for Relationships")
#st.write(df_r)

#filter by observer
#st.subheader("Observer")
#observer_frames_r = filter_by('observer', select_data_r, df_r, 'c')
#observer_full_r = observer_frames_r[0]
#observer_sub_r = observer_frames_r[1]
#st.write(observer_full_r)

#filter by type with or without observer
#st.subheader("Relationship Type")
#rt_frames = filter_by('observer', observer_sub_r, observer_full_r, 'd')
#rt_full = observer_frames_r[0]
#rt_sub = observer_frames_r[1]
#st.write(rt_full)


#st.subheader("Model Musical Type")

#mmt_list = rt_full['model_observation.musical_type'].unique().tolist()
#mmt_list = ["Fuga"]
#mmt_selected = st.radio('', mmt_list)
#mmt_selected_list = list(mmt_selected)

#if mmt_selected_list:
#    masked_mmt = rt_full['model_observation.musical_type'].isin([mmt_selected])
#    mmt_full = rt_full[masked_mmt]

#else:
#    mmt_full = rt_full


#st.markdown("relationships at this point:")
#st.write(mmt_full)

#m_col_list = [col for col in mmt_full.columns if 'model_observation.details' in col ]
#st.write(m_col_list)


#st.subheader("Derivative Musical Type")

#dmt_list = mmt_full['derivative_observation.musical_type'].unique().tolist()
#dmt_selected = st.radio('', dmt_list, key="e")
#dmt_selected_list = list(dmt_selected)

#if dmt_selected_list:
#    masked_dmt = mmt_full['derivative_observation.musical_type'].isin([dmt_selected])
#    dmt_full = mmt_full[masked_dmt]

#else:
#    dmt_full = mmt_full


#st.markdown("relationships at this point:")
#st.write(dmt_full)

#d_col_list = [col for col in dmt_full.columns if 'derivative_observation.details' in col ]
#st.write(d_col_list)

#TODO: Visualize data in df
#st.subheader("Graphical representation of data in observations")
#hist_values=np.histogram(df['musical_type'].tolist())
#st.bar_chart(hist_values)



st.markdown("---")
st.header("RELATIONSHIP VIEWER")

order = st.radio("Select order to filter data: ", ('Pieces then Relationship Type', 'Relationship Type then Pieces'))
if (order == 'Pieces then Relationship Type'):
    #filter by pieces
    st.subheader("Model Piece")
    mpiece_frames = filter_by("model_observation.piece.piece_id", select_data_r, df_r, 'c')
    mpiece_full = mpiece_frames[0]
    mpiece_sub = mpiece_frames[1]
    #st.write(piece_full)
    #st.write(piece_sub)

    st.subheader("Derivative Piece")
    dpiece_frames = filter_by("derivative_observation.piece.piece_id", mpiece_sub, mpiece_full, 'd')
    dpiece_full = dpiece_frames[0]
    dpiece_sub = dpiece_frames[1]

    #filter by type with or without pieces
    st.subheader("Relationship Type")
    rt_frames = filter_by('relationship_type', dpiece_sub, dpiece_full, 'e')
    rt_full = rt_frames[0]
    rt_sub = rt_frames[1]
    st.markdown('Resulting relationships:')
    #st.write(rt_full)
    st.write(rt_sub)
else:
    #filter by musical type
    st.subheader("Relationship Type")
    rt_frames = filter_by('relationship_type', select_data_r, df_r, 'x')
    rt_full = rt_frames[0]
    rt_sub = rt_frames[1]
    #st.write(rt_full)

    #filter by piece with or without musical type
    st.subheader("Model Piece")
    mpiece_frames = filter_by('model_observation.piece.piece_id', rt_sub, rt_full, 'w')
    mpiece_full = mpiece_frames[0]
    mpiece_sub = mpiece_frames[1]
    #st.write(mpiece_sub)

    st.subheader("Derivative Piece")
    dpiece_frames = filter_by('derivative_observation.piece.piece_id', mpiece_sub, mpiece_full, 'v')
    dpiece_full = dpiece_frames[0]
    dpiece_sub = dpiece_frames[1]
    st.markdown('Resulting relationships:')
    st.write(dpiece_sub)