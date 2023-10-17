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
import plotly 
from plotly.graph_objs import *


#### SETTING MATPLOTLIB PARAMS ######
plt.rcParams.update({'text.color': "white",
                    'axes.labelcolor': "white",
                    'axes.edgecolor': 'white',
                    'xtick.color': 'white',
                    'ytick.color': 'white',
                    'figure.facecolor': '0F1116',
                    'axes.facecolor': '0F1116'})



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





col1, col2= st.columns([1,4])

col1.subheader("Project Background")

col1.write("Welcome to the emissions data web app, developed by Mikayla Norton for the CMSE 830 midterm project. This web app serves to demonstrate changes in annual emissions by region and allow the user to generate key findings by country or emissions type over time. Please utilize the selection criteria below to narrow focused visualizations below or manage the slider to the right to view the bigger picture.")


col1.subheader("Data Pre-Processing")

col1.write("With any new dataset, non-visual exploration of missingness and surface-level trends are a must. Imputation of missingness was excluded from the body of the app, however a trend was determined that years of no record for emissions were logged as a missing value. A simple imputation to these values set them to zero to show the start of a baseline trend. It is important to note that there were still likely low-level emissions during this time, but due to the nature of the exponential curve trends, zero-imputation was deemed most effective.")

col1.write("In dealing with geographic data with shape file exclusions, the requirements for generating meaningful geographic data required some creativity. To create the primary Plotly Express feature, the data set was merged with a shapefile dataset, as well as categorization data for iso-3 abbreviations and respective regions.")

col1.subheader("Directions")
col1.write("In the first figure to the right, customize the features by selecting the year for which per capita emissions information should be visualized. The plot will refresh accordingly, with bubbles corresponding to emissions level and hover-over information detailing numerics.")
col1.write("In the next section, two summary figures outline the top 10 emitters globally across all dates, and the pollutant source contributing most to emissions, internationally.")
col1.write("Lastly, investigative analytics in section 3 provides two feature figures to compare nations and/or emissions types. In the first figure of this section, the user may select a emission category, a date range, and multiple countries to visualize the trends year over year. In the second figure, one country may be selected to generate a stacked barplot of pollutant distribution annually. By hovering over the figure, detailed numerics per year and category can be viewed.")


col1.subheader("Objective & Findings")

col1.write("As greenhouse gas emissions continue to play a significantly detrimental role in global climate issues, it is important to investigate key contributors, both in emission sources and national participants. The overview of nations with the highest level of pollution and changes in these emitter rankings acted as top objectives of this web app.")
col1.write("It can be observed that gas plays an unmatched role in greenhouse gas emissions globally. The United States, China, and Russia also act as the highest emitters of these pollutants over the full date range. There has been a noticeable rise in emissions since the mid 1900s, a trend spanning across most nations, however, each nation has a respective difference in the key contributing pollutant to the overall emissions.")

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

########### WORLD MAP ############
fig = px.scatter_geo(map_and_stats, locations="iso3",
                    size="Per Capita",hover_name="Country",color="Major Region", width=900)
fig.update_geos(showcoastlines=True, coastlinecolor="white", coastlinewidth=1)

fig.update_layout(geo=dict(bgcolor='rgba(15, 17, 22,1)'))

col2.plotly_chart(fig)
col2.divider()

########### TOP CONTRIBUTORS PLOTTING ###########
col2.header("Significant Global Emissions Contributions")
col2a, col2b = col2.columns(2)

places = list(df.groupby('Country').sum().sort_values(by='Total',ascending=False).index)
vals = list(df.groupby('Country').sum().sort_values(by='Total',ascending=False)['Total'])

fig, ax = plt.subplots(1,figsize=(12, 7))
# sns.set_style('darkgrid')
sns.barplot(x=places[:10],y=vals[:10],palette='crest',edgecolor='.2', ax=ax)
plt.xlabel("Country")
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
col2b.subheader('Strongest Contributing Emissions Globally')
col2b.pyplot(fig)
col2.divider()


col2.header("Customizable Investigative Emissions Analytics")
############# A - SELECTION CRITERIA ##########
col2a, col2b = col2.columns([1,3])
col2a.subheader("Selection Criteria")
types = col2a.selectbox("Choose emission type", list(df.columns[2:10])) #emissions type

start = col2a.number_input("Please enter a start date", min(df["Year"]), max(df["Year"])) #start date
end = col2a.number_input("Please enter an end date", min(df["Year"]), max(df["Year"]), value=max(df["Year"])) #end date

if start > end:
    col2a.error("Start date cannot be later than end date") 


countries = col2a.multiselect(
    "Choose countries", list(df.index.unique()), ["China", "USA"] #countries selection
)

if not countries:
    col2a.error("Please select at least one country.")
else:
    data = df_country_data[df_country_data["Country"].isin(list(countries))]


dates = list(range(start, end+1))

######## TIME SERIES PLOTTING ###########


col2b.subheader("Filtered time series plot of select countries between " + str(round(start)) + " and " + str(round(end)) + " for " + types +" data.")
cm = pl.get_cmap('Greens')


def update_colors(ax):
    lines = ax.lines
    colors = cm(np.linspace(0, 0.7, len(lines)))
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

col2b.pyplot(fig)

col2.divider()


############# B - SELECTION CRITERIA ##########
col2a, col2b = col2.columns([1,3])

col2a.subheader("Selection Criteria")
# types = col2a.selectbox("Choose emission type", list(df.columns[2:10])) #emissions type

# start = col2a.number_input("Please enter a start date", min(df["Year"]), max(df["Year"])) #start date
# end = col2a.number_input("Please enter an end date", min(df["Year"]), max(df["Year"]), value=max(df["Year"])) #end date

# if start > end:
#     col2a.error("Start date cannot be later than end date") 


country = col2a.selectbox(
    "Choose country", list(df.index.unique()),index=220) #country selection

if not country:
    col2a.error("Please select at least one country.")
else:
    data = df_country_data[df_country_data["Country"] == country]
    data.drop(columns=['Total', 'Per Capita'], inplace=True)
    #data.set_index('Year', inplace=True)


######## BAR PLOTTING ###########
col2b.subheader("Stacked Bar of Emissions Types for " + country)

# colors = cm(np.linspace(0.3, 1, len(list(df.columns[2:10]))))
# data.plot(kind='bar', stacked=True, color=colors, ax=ax)
# start, end = ax.get_xlim()
# ax.xaxis.set_ticks(np.arange(start, end, 25), labels=np.arange(1750, 2021, 25))
# col2b.pyplot(fig)
cubhelix = px.colors.qualitative.Prism

colors = {"Coal": cubhelix[0], "Oil": cubhelix[1], "Gas": cubhelix[2], "Cement": cubhelix[3], "Flaring": cubhelix[4], "Other": cubhelix[5]}
fig = px.bar(data, x="Year", y=["Coal", "Oil", "Gas", "Cement", "Flaring", "Other"], color_discrete_map=colors, width=900)
fig.update_layout(yaxis_title="Emissions")
col2b.plotly_chart(fig)

