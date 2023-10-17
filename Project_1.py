import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
import copy
import pylab as pl
import numpy as np
import seaborn as sns

st.set_page_config(layout="wide")
st.title("CMSE 830 Midterm - Geographic Annual Emissions")
df = pd.read_csv("Emissions/GCB2022v27_MtCO2_flat.csv")
df_country_data = df.copy()
############# CLEANING ##############
world = df[df['ISO 3166-1 alpha-3']=='WLD']
df = df[df['Country']!='Global']


transport = df[df['Country']=='International Transport']
df = df[df['Country']!='International Transport']
df = df.set_index("Country")
df.fillna(0, inplace=True)

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





col1, col2= st.columns([1,3])
# col1.title('Country Emissions')

# col2.title('Annual Total Emissions')

# col3.title('Emissions by Type')

col1.subheader("Project Background")

col1.write("Welcome to the emissions data web app, developed by Mikayla Norton for the CMSE 830 midterm project. This web app serves to demonstrate changes in annual emissions by region and allow the user to generate key findings by country or emissions type over time. Please utilize the selection criteria below to narrow focused visualizations below or manage the slider to the right to view the bigger picture.")


col1.subheader("Data Pre-Processing")

col1.write("With any new dataset, non-visual exploration of missingness and surface-level trends are a must. Imputation of missingness was excluded from the body of the app, however a trend was determined that years of no record for emissions were logged as a missing value. A simple imputation to these values set them to zero to show the start of a baseline trend. It is important to note that there were still likely low-level emissions during this time, but due to the nature of the exponential curve trends, zero-imputation was deemed most effective.")

col1.write("In dealing with geographic data with shape file exclusions, the requirements for generating meaningful geographic data required some creativity. To create the primary Plotly Express feature, the data set was merged with a shapefile dataset, as well as categorization data for iso-3 abbreviations and respective regions.")


col1.subheader("Selection Criteria")
types = col1.selectbox("Choose emission type", list(df.columns[2:10])) #emissions type

start = col1.number_input("Please enter a start date", min(df["Year"]), max(df["Year"])) #start date
end = col1.number_input("Please enter an end date", min(df["Year"]), max(df["Year"]), value=max(df["Year"])) #end date

if start > end:
    col2.error("Start date cannot be later than end date") 


countries = col1.multiselect(
    "Choose countries", list(df.index.unique()), ["China", "USA"] #countries selection
)

if not countries:
    col1.error("Please select at least one country.")
else:
    data = df_country_data[df_country_data["Country"].isin(list(countries))]


dates = list(range(start, end+1))


########## PLOTTING ###############
world_map = gpd.read_file("world-administrative-boundaries/world-administrative-boundaries.shp")
regions = pd.read_csv("continents2.csv")


col2.header("Annual Per Capita Emissions")
y = col2.slider("Year Selection", min(df["Year"]), max(df["Year"]), step = 1, value=2021)

df = df.rename(columns={'Alpha-3 code': 'alpha-3'})
regions_df = df.merge(regions, on="alpha-3")

regions_df = regions_df.rename(columns={'alpha-3': 'iso3'})
dfyear = regions_df.loc[regions_df["Year"] == y]

map_and_stats=world_map.merge(dfyear, on="iso3")
map_and_stats = map_and_stats.rename(columns={'region_y': 'Major Region'})
map_and_stats = map_and_stats.rename(columns={'name_x': 'Country'})

# fig, ax = plt.subplots(1, figsize=(12, 16))
# plt.rcParams['axes.facecolor'] = 'white'
# plt.xticks(rotation=90)
# plt.axis('off')

# map_and_stats.plot(column="Per Capita", cmap="Reds", linewidth=0.4, ax=ax, edgecolor=".4", vmin=0, vmax=50, legend=True, legend_kwds={'shrink': 0.3})

# col2.pyplot(fig)

########### WORLD MAP ############
fig = px.scatter_geo(map_and_stats, locations="iso3",
                    size="Per Capita",hover_name="Country",color="Major Region", width=900)
col2.plotly_chart(fig)

########### TOP CONTRIBUTORS PLOTTING ###########
col2.header("Significant Global Emissions Contributions")
col2a, col2b = col2.columns(2)

places = list(df.groupby('Country').sum().sort_values(by='Total',ascending=False).index)
vals = list(df.groupby('Country').sum().sort_values(by='Total',ascending=False)['Total'])

fig, ax = plt.subplots(1,figsize=(12, 7))
# sns.set_style('darkgrid')
sns.barplot(x=places[:10],y=vals[:10],palette='crest',edgecolor='.2', ax=ax)
col2a.subheader("Top 10 Contributors to Global Emissions")

col2a.pyplot(fig)

################################################

cols = ['Coal', 'Oil', 'Gas','Cement', 'Flaring', 'Other']
world_data_past_10 = world[-10:]
values_world = []
for i in cols:
    values_world.append(world_data_past_10.iloc[9][str(i)]-world_data_past_10.iloc[0][str(i)])

dz = pd.DataFrame({"Type": cols, 
                "Values": values_world})

fig, ax = plt.subplots(1,figsize=(12, 7))
sns.barplot(x='Type',y='Values', data=dz,order=dz.sort_values('Values',ascending = False).Type, palette='cubehelix',edgecolor='.3', ax=ax)
col2b.subheader('Strongest Contributing Emissions Type Globally')
col2b.pyplot(fig)




######## FILTERED PLOTTING ###########

col2.header("Filtered time series plot of select countries between " + str(round(start)) + " and " + str(round(end)) + " for " + types +" data.")
cm = pl.get_cmap('Greens')


def update_colors(ax):
    lines = ax.lines
    colors = cm(np.linspace(0.3, 1, len(lines)))
    for line, c in zip(lines, colors):
        line.set_color(c)


df_year_filter = data[data["Year"].isin(dates)]

fig, ax = plt.subplots(1,figsize=(12, 5))
for c in countries:
    z = df_year_filter[df_year_filter["Country"]==c].copy()
    plt.plot(round(z["Year"]), z[types],  label=c)
    plt.xlabel("Year")
    plt.ylabel(types + " Emissions Data")
    update_colors(ax)
    plt.legend()

col2.pyplot(fig)

col2.write("Still to come after HW 6 update - addition of more geographic mapping, interactive features, clean up")

