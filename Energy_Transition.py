import pandas as pd
import numpy as np
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
import openpyxl

# Set visualization options
pd.set_option('display.max_columns',200)
pd.set_option('display.width', 32000)

# Data for GDP from https://data.worldbank.org/indicator/NY.GDP.MKTP.CD

# Create the necessary dataframes: Production, Consumption and GDP
df_consumption = pd.read_csv('modern-renewable-energy-consumption.csv')
df_production = pd.read_csv('modern-renewable-prod.csv')
df_gdp = pd.ExcelFile('GDP year country.xlsx')
df_gdp = pd.read_excel(df_gdp,'Data')

# Drop the unnecessary columns by name
df_gdp.drop(df_gdp.loc[:, '1960':'1999'].columns,axis=1, inplace=True)
# Drop the unnecessary columns by location
df_gdp.drop(df_gdp.iloc[:, 26:].columns,axis=1, inplace=True)

# Merge the dataframes of production and consumption on columns
df_prodandcons = pd.merge(df_consumption,df_production, on=("Entity", "Code", "Year"))
# Rename column
df_prodandcons.rename(columns={"Entity": "Country Name"}, inplace=True)

# List of countries in production and consumption
listPC=df_prodandcons['Country Name'].unique().tolist()

# Transpose some columns of the dataframe
df_gdp2= df_gdp.melt(['Country Name', 'Country Code','Indicator Name', 'Indicator Code'], var_name="Year")
# Change data type to int
df_gdp2['Year'] = df_gdp2['Year'].astype('int')
# Replace values in Country Name
df_gdp2['Country Name'] = df_gdp2['Country Name'].replace(['Egypt, Arab Rep.', 'Hong Kong SAR, China',
                                                            'Iran, Islamic Rep.', 'South Korea, Rep.', 'Venezuela, RB'],
                                                          ['Egypt', 'Hong Kong', 'Iran', 'Korea', 'Venezuela'])

# List of countries in GDP
listGDP=df_gdp2['Country Name'].unique().tolist()


# List of countries in list of energy not in GDP and viceversa

listPCnotGDP =[]
listGDPnotPC = []
for element in listPC:
    if element not in listGDP:
        listPCnotGDP.append(element)

for element in listGDP:
    if element not in listPC:
        listGDPnotPC.append(element)

print(listPCnotGDP)
print(listGDPnotPC)

# Merge the dataframes of production/consumption and GDP
df_PCGDP = pd.merge(df_prodandcons,df_gdp2, how='inner', left_on=['Country Name', 'Year'],right_on=['Country Name', 'Year'])

# Drop unnecessary columns
df_PCGDP.drop(df_gdp.loc[:, 'Country Code':'Indicator Code'].columns,axis=1, inplace=True)

# Rename columns
df_PCGDP.rename(columns={'Country Name':'Country_Name','value':'GDP MUSD','Wind Generation - TWh':"Wind Generation Consumption (TWh)",
                         'Solar Generation - TWh':'Solar Generation Consumption (TWh)',
                         'Geo Biomass Other - TWh':'Geo Biomass Other Consumption (TWh)',
                         'Hydro Generation - TWh':'Hydro Generation Consumption (TWh)',
                         'Electricity from wind (TWh)': 'Electricity Production from wind (TWh)',
                         'Electricity from hydro (TWh)':'Electricity Production from hydro (TWh)',
                         'Electricity from solar (TWh)':'Electricity Production from solar (TWh)',
                         'Electricity from other renewables including bioenergy (TWh)': 'Electricity from other renewables including bioenergy (TWh)'},
                inplace=True)

# Add total consumption and total production columns
df_PCGDP["Total Consumption"]=df_PCGDP['Wind Generation Consumption (TWh)']+df_PCGDP['Solar Generation Consumption (TWh)']+\
                              df_PCGDP['Geo Biomass Other Consumption (TWh)']+df_PCGDP['Hydro Generation Consumption (TWh)']
df_PCGDP['Total Production']=df_PCGDP['Electricity Production from wind (TWh)']+df_PCGDP['Electricity Production from hydro (TWh)']+\
                             df_PCGDP['Electricity Production from solar (TWh)']+df_PCGDP['Electricity from other renewables including bioenergy (TWh)']

# Divide column GDP into millions
df_PCGDP['GDP MUSD']= df_PCGDP['GDP MUSD']/1000000

print(df_PCGDP.head())

# Number of countries in analysis
print(f"Number of countries analyzed: {df_PCGDP['Country_Name'].nunique()}")

df2020 = df_PCGDP[df_PCGDP['Year']==2020]
df2020=df2020.sort_values('Total Production',axis=0,ascending=False)

df2020.drop(labels=[1574], inplace=True)
df2020.drop(labels=[272], inplace=True)
df2020.drop(labels=[1406], inplace=True)
df2020.drop(labels=[965], inplace=True)

df2020=df2020.head(10)
print(df2020)

top_ten_countries=['United States', 'Brazil', 'Canada', 'India', 'Japan', 'Norway','United Kingdom','France','Italy']

df_prodtrend = df_PCGDP
df_prodtrend.drop(df_prodtrend.columns[[1,3,4,5,6,11,12]],axis=1,inplace=True)
df_prodtrend=df_prodtrend[~df_prodtrend['Country_Name'].isin(top_ten_countries)==False]
print(df_prodtrend)

# df_gdp.drop(df_gdp.iloc[:, 26:].columns,axis=1, inplace=True)

#df2020.to_excel('Energy Transition 2020.xlsx')


# ---------------Streamlit data app--------------
# Page icon from https://www.webfx.com/tools/emoji-cheat-sheet/

st.set_page_config(page_title="Renewable Energy and GDP by country",
                   page_icon=':evergreen_tree:',
                   layout='wide',
                   )


# ------- SIDEBAR-------------

st.sidebar.header("Please filter:")

country = st.sidebar.multiselect(
    "Select the Country:",
    options=df2020['Country_Name'].unique(),
    default=df2020['Country_Name'].unique()
)


df_selection = df2020.query('Country_Name == @country')
df_selection2 = df_prodtrend.query('Country_Name == @country')


# ------MAINPAGE-------

st.title(":bar_chart: Renewable Energy (top 10 countries)")
st.markdown("##")

# Subheader

total_production = int(df_selection['Total Production'].sum())
print(total_production)
average_production = round(df_selection['Total Production'].sum())
top10_production = int(df2020['Total Production'].sum())
part_production = average_production/top10_production
part_production = "{:.0%}".format(part_production)
GDP_selected = round(df_selection['GDP MUSD'].sum()/1e6)
#star = ":star:" * int(round(average_production, 0))

left_column, middle_column,right_column = st.columns(3)

with left_column:
    st.subheader("Total Production of selected countries:")
    st.subheader(f":zap: TWh {total_production:,}")

with middle_column:
    st.subheader("Selected countries participation in production")
    st.subheader(f" {part_production}")

with right_column:
    st.subheader("Selected countries GDP in Trillion USD")
    st.subheader(f":heavy_dollar_sign: {GDP_selected}")


st.markdown("---")

# ------BAR CHARTS-------

# ----WIND------

fig_wind_generation = px.bar(
    df_selection,
    x='Electricity Production from wind (TWh)',
    y='Country_Name',
    orientation='h',
    title='<b>Wind Production in Twh <b>',
    color = 'Country_Name',
    text_auto= 'True',
)

fig_wind_generation.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    showlegend=False,
)

fig_wind_generation.update_xaxes(title_text='Twh')
fig_wind_generation.update_yaxes(title_text='Country')

#-----HYDRO------

fig_hydro_generation = px.bar(
    df_selection,
    x='Electricity Production from hydro (TWh)',
    y='Country_Name',
    orientation='h',
    title='<b>Hydro Production in Twh <b>',
    color = 'Country_Name',
    text_auto= 'True',
)

fig_hydro_generation.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    showlegend=False
)

fig_hydro_generation.update_xaxes(title_text='Twh')
fig_hydro_generation.update_yaxes(title_text='Country')

#-----SOLAR------

fig_solar_generation = px.bar(
    df_selection,
    x='Electricity Production from solar (TWh)',
    y='Country_Name',
    orientation='h',
    title='<b>Solar Production in Twh <b>',
    color = 'Country_Name',
    text_auto= 'True',
)

fig_solar_generation.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    showlegend=False
)

fig_solar_generation.update_xaxes(title_text='Twh')
fig_solar_generation.update_yaxes(title_text='Country')

#-----OTHER------

fig_other_generation = px.bar(
    df_selection,
    x='Electricity from other renewables including bioenergy (TWh)',
    y='Country_Name',
    orientation='h',
    title='<b>Other Production in Twh <b>',
    color = 'Country_Name',
    text_auto= 'True',
)

fig_other_generation.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    showlegend=False
)

fig_other_generation.update_xaxes(title_text='Twh')
fig_other_generation.update_yaxes(title_text='Country')


left_chart, left_center_chart,right_center_chart,right_chart = st.columns(4)

left_chart.plotly_chart(fig_wind_generation, use_container_width=True)
left_center_chart.plotly_chart(fig_hydro_generation, use_container_width=True)
right_center_chart.plotly_chart(fig_solar_generation, use_container_width=True)
right_chart.plotly_chart(fig_other_generation, use_container_width=True)

st.markdown("---")

#------WATERFALL CHART-----

waterfall=go.Figure(go.Waterfall(
    name="WHAAAAAT", orientation='v',
    measure=['relative', 'relative','relative','relative', 'total'],
    x=['Wind','Hydro','Solar','Other','Total'],
    text=[int(df_selection['Electricity Production from wind (TWh)'].sum()),int(df_selection['Electricity Production from hydro (TWh)'].sum()),
       int(df_selection['Electricity Production from solar (TWh)'].sum()),int(df_selection['Electricity from other renewables including bioenergy (TWh)'].sum()),
       int(df_selection['Total Production'].sum())],
    textposition='outside',
    y=[df_selection['Electricity Production from wind (TWh)'].sum(),df_selection['Electricity Production from hydro (TWh)'].sum(),
       df_selection['Electricity Production from solar (TWh)'].sum(),df_selection['Electricity from other renewables including bioenergy (TWh)'].sum(),
       df_selection['Total Production'].sum()]
))

waterfall.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    yaxis=(dict(showgrid=False)),
    showlegend=False,
    title="<b>Total Energy production by Technology in Twh<b>"
)


source = st.sidebar.selectbox("Select the technology",["Total Production","Electricity Production from wind (TWh)","Electricity Production from hydro (TWh)",
                                "Electricity Production from solar (TWh)","Electricity from other renewables including bioenergy (TWh)"
                                ])

fig_growth=px.line(df_selection2, x='Year', y=source, color='Country_Name', labels={"Total Production":"Total Production in Twh"})
fig_growth.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False)),
    yaxis=(dict(showgrid=False)),
    showlegend=True,
    title="<b>Evolution of renewable energy production by Technology<b>"
)

bottom_left,bottom_right = st.columns(2)

bottom_left.plotly_chart(waterfall, use_container_width=True)
bottom_right.plotly_chart(fig_growth,use_container_width=True)

st.markdown("---")


df = pd.read_excel('locations.xlsx')

df_f=pd.merge(df,df_selection, on='Country_Name', how='inner')


fig_map = px.scatter_mapbox(df_f, lat='latitude', lon='longitude', size=source,
                            color='Country_Name',zoom=1, mapbox_style='open-street-map',
                            title="<b>Map of World Energy Production by Technology (TWh)<b>",
                            size_max=30)



last_section = st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

'''Data From World Bank, IRENA and Kaggle'''


#last_sectionl.plotly_chart(waterfall, use_container_width=True)
#last_sectionr.plotly_chart(fig_growth, use_container_width=True)


# ------DATAFRAME---------

# st.dataframe(df_selection)

