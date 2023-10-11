import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")
df = pd.read_csv("Emissions/GCB2022v27_MtCO2_flat.csv")
df = df.set_index("Country")

latLon = pd.read_csv("https://gist.githubusercontent.com/tadast/8827699/raw/f5cac3d42d16b78348610fc4ec301e9234f82821/countries_codes_and_coordinates.csv")
for i in range(len(latLon["Latitude (average)"])):
    latLon["Latitude (average)"][i]=latLon["Latitude (average)"][i].replace('"', '')
    latLon["Longitude (average)"][i]=latLon["Longitude (average)"][i].replace('"', '')
    latLon["Alpha-3 code"][i]=latLon["Alpha-3 code"][i].replace('"', '').strip()
latLon["Latitude (average)"] = latLon["Latitude (average)"].astype(float)
latLon["Longitude (average)"] = latLon["Longitude (average)"].astype(float)

latLon = latLon[["Alpha-3 code", "Latitude (average)", "Longitude (average)"]]
df = df.rename(columns={'ISO 3166-1 alpha-3': 'Alpha-3 code'})
df2 = df.merge(latLon, how="left", on="Alpha-3 code")
df2["Country"] = df.reset_index()["Country"]
df2.set_index("Country")


col1, col2, col3 = st.columns(3)
# col1.title('Country Emissions')

# col2.title('Annual Total Emissions')

# col3.title('Emissions by Type')

st.subheader('Raw data')
st.write(df)

types = col1.selectbox("Choose emission type", list(df.columns[2:8]))

start = col1.number_input("Please enter a start date", min(df["Year"]), max(df["Year"]))
end = col1.number_input("Please enter an end date", min(df["Year"]), max(df["Year"]))
if start > end:
    col2.error("Start date cannot be later than end date")


countries = col1.multiselect(
    "Choose countries", list(df.index.unique()), ["China", "USA"]
)
if not countries:
    col1.error("Please select at least one country.")
else:
    data = df2.set_index("Country")
    data = data.loc[countries]
    # fig = px.scatter_mapbox(data, lat="Latitude (average)", lon="Longitude (average)", hover_name="Alpha-3 code", hover_data='Total', zoom=1)
    # fig.update_layout(mapbox_style="open-street-map")
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

dates = list(range(start, end+1))
fig, ax = plt.subplots(figsize=(11, 9))
for i in countries:
    df_copy = df.loc[df["Country"]==i]

# fig = plt.plot(dates, df[types])


# data_load_state = st.text('Loading data...')
# df = pd.read_csv("Emissions/GCB2022v27_MtCO2_flat.csv")
# df = df.set_index("Country")

# #data_load_state.text('Loading data...done!')

# st.subheader('Raw data')
# st.write(df)



    # col1.plotly_chart(fig)
    # fig, x = plt.subplots()
    # for index, row in data.iterrows():
    #     x.plot(row, label=index)
    # x.legend()
    # st.pyplot(fig)






