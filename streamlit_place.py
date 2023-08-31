import streamlit as st
import plotly.express as px
from urllib.parse import quote
import pandas as pd
import requests
import json
import time 
import plotly.express as px
import leafmap.foliumap as leafmap
import os

#import leafmap.kepler as leafmap

api_key = os.getenv('api_key')


st.set_page_config(page_title = 'cashback',
                  page_icon = ':moneybag:',
                   layout = 'wide'
                  )


if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

def disable():
    st.session_state["disabled"] = True



search_text = st.text_input(
    "Search popular attractions/restaurants via google map 👇",
    disabled=st.session_state.disabled, 
    on_change=disable,
    placeholder="Attractions in Tokyo")

print(st.session_state.disabled)


c1,c2 = st.columns(2)
with c1:
    review_amount_filter= st.number_input(
        "Select the minimum reviews amount 👇",500)
with c2:
    review_filter= st.number_input(
        "Select the minimum reviews (1-5) 👇",4.3)    



def convert_df(df):
    return df_selection.to_csv(index=False).encode('utf-8')

query_text = quote(search_text)

if st.session_state.disabled == False:
    st.write("Start seaching attractions/restaurants")
else:
    places = requests.get(f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={query_text}&language=en&key={api_key}')
# Convert the response to a JSON object.
    places_results = json.loads(places.text)['results']
    w = list(places_results)

    while True:
        if 'next_page_token' in json.loads(places.text):
            token = json.loads(places.text)["next_page_token"]
            print(token[-5:-1])
            places = requests.get(f'https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={token}&key={api_key}')
            test = json.loads(places.text)['results']   
        
            time.sleep(5)
        
            w.extend(test)
            print(len(w))

            print('successful')
        else:
            print('stop')
            break

    final = pd.DataFrame(w)
    final = final.sort_values(by="user_ratings_total",ascending=False)
    final.reset_index(drop=True,inplace=True)
    print(final.columns)



    df_selection = final.query(
        "user_ratings_total >= @review_amount_filter &  rating>= @review_filter" 
    )

    df_selection["lat"] = df_selection["geometry"].apply(lambda x: x["location"]["lat"])

    df_selection["lng"] = df_selection["geometry"].apply(lambda x: x["location"]["lng"])
    df_selection.reset_index(drop=True,inplace=True)


    df_selection = df_selection[["name","rating","user_ratings_total","lat","lng","formatted_address"]]


    st.dataframe(df_selection)


    






    c_center = [sum(df_selection["lat"])/len(df_selection["lat"]),sum(df_selection["lng"]/len(df_selection["lng"]))]
    m = leafmap.Map(center=c_center, zoom=12, tiles="stamentoner")


    m.add_circle_markers_from_xy(df_selection, x="lng", y="lat")
    m.to_streamlit()
    #m.popup()


    print("_______end________")

    csv = convert_df(final)

    st.download_button(
   "Press to Download",
   csv,
   "file.csv",
   "text/csv",
   key='download-csv'
    ) 






#""" url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&fields=name%2Crating%2Cformatted_phone_number&key=YOUR_API_KEY"

#payload={}
#headers = {}

#response = requests.request("GET", url, headers=headers, data=payload)

#print(response.text) """