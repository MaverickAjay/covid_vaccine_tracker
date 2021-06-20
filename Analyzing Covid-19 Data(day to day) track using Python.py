#!/usr/bin/env python
# coding: utf-8

# # Analyzing Covid-19 Data(day to day) track using Python
# 

# In[1]:


#importing necessary libraries
from datetime import datetime 
import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import warnings
warnings.filterwarnings("ignore")


# ## Reading Data

# In[2]:


df=pd.read_csv('final_input2.csv')


# In[3]:


df.head()


# In[4]:


#droping unwanted columns
df1=df.drop(['Unnamed: 7','Unnamed: 8','Unnamed: 9','Unnamed: 10'], axis = 1)


# In[5]:


df1.head()


# In[6]:


df1.shape


# In[7]:


df1.describe()


# In[8]:


df1.info()


# In[9]:


df["Date"].max(), df["Date"].min()


# ### Geodataframe

# In[10]:


#The co-orinate reference system value is obtained from http://epsg.io
crs="EPSG:4326"


# In[11]:


gdf = gpd.GeoDataFrame(df1, crs=crs, geometry=gpd.points_from_xy(df1.Longitude, df.Latitude))
gdf.head()


# In[12]:


gdf.plot(figsize=(12,10))


# # Plotting Maps

# In[13]:


ctx.providers.keys()


# In[14]:


ctx.providers.Esri.keys()


# In[16]:


fig, ax = plt.subplots(figsize=(14, 12))
gdf[gdf["Date"] == '2020-03-30'].to_crs(epsg=3857).plot(ax=ax, color="red", edgecolor="white")
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite) 
plt.title("Deceased Map -  2020-03-30", fontsize=30, fontname="Palatino Linotype", color="grey")
ax.axis("off")
plt.show()


# # Bubble Maps

# In[17]:


fig, ax = plt.subplots(figsize=(14, 12))
gdf[gdf["Date"] == '2020-03-30'].to_crs(epsg=3857).plot(ax=ax, color="red", alpha=.4,  markersize="Deaths")
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite) 
plt.title("Deceased Bubble Map - 2020-03-30", fontsize=30, fontname="Palatino Linotype", color="grey")
ax.axis("off")
plt.show()


# In[18]:


#calculating Normalized mean Death
gdf["Normalized_mean_death"]=((gdf["Deaths"]-gdf['Deaths'].min())/(gdf["Deaths"].max()-gdf["Deaths"].min()))*100


# In[19]:


gdf.tail()


# In[20]:


fig, ax = plt.subplots(figsize=(14, 12))
gdf[gdf["Date"] == '2021-01-01'].to_crs(epsg=3857).plot(ax=ax, color="red", alpha=.7,  markersize="Normalized_mean_death")
ctx.add_basemap(ax, source=ctx.providers.Stamen.TonerLite) 
plt.title(" Covid-19 -  2021-01-01 ", fontsize=30, fontname="Palatino Linotype", color="grey")
#ax.axis("off")
plt.show()


# # Day to Day Covid-19 Track
# 

# In[21]:


formated_gdf = df1.groupby(['Date', 'Country'])['Confirmed', 'Deaths'].max()
formated_gdf = formated_gdf.reset_index()
formated_gdf['Date'] = pd.to_datetime(formated_gdf['Date'])
formated_gdf['Date'] = formated_gdf['Date'].dt.strftime('%m/%d/%Y')
formated_gdf['size'] = formated_gdf['Confirmed'].pow(0.3)

fig = px.scatter_geo(formated_gdf, locations="Country", locationmode='country names', 
                     color="Confirmed", size='size', hover_name="Country",
                     range_color= [0, max(formated_gdf['Confirmed'])+2], animation_frame="Date", 
                     title='Spread over time')
fig.update(layout_coloraxis_showscale=False)
fig.show()


# # Covid vaccines used by country worldwide

# ## Reading and Preparing Data

# In[22]:


manu = pd.read_csv("country_vaccinations_by_manufacturer.csv")
manu['date'] = pd.to_datetime(manu.date)

country = pd.read_csv("country_vaccinations.csv")
country['date'] = pd.to_datetime(country.date)


# In[23]:


manu.head()


# In[24]:


manu.location.unique()


# In[25]:


#temporarily set max max_colwidth to None
pd.set_option('display.max_colwidth', None)
country[['country', 'date', 'vaccines']].head()


# In[26]:


#Now, I want to keep the best-known vaccins (Pfizer, Moderna, AstraZeneca and Johnson&Johnson) as they are and group lesser-known brands into the countries where they are made.

#strip text
country['vaccines'] = country['vaccines'].str.replace("/Beijing|/Wuhan|/HayatVax|/BioNTech|Oxford/", "", regex=True)

#replace with Chinese vaccins
country['vaccines'] = country['vaccines'].str.replace("Sinopharm|BBIBP-CorV|Sinovac|CanSino|RBD-Dimer", "Chinese", regex=True)

#replace with Russian vaccins
country['vaccines'] = country['vaccines'].str.replace("EpiVacCorona|Sputnik V", "Russian", regex=True)

#replace with Cuban vaccins
country['vaccines'] = country['vaccines'].str.replace("Soberana02|Abdala", "Cuban", regex=True)

#replace some others
to_replace = {'Covaxin': 'Indian',
              'QazVac': 'Kazachstan'}
country['vaccines'] = country['vaccines'].replace(to_replace, regex=True)


# In[27]:


#making a list of all vaccins
vac_list = [x.split(", ") for x in country.vaccines.values]
vaccines = [item for elem in vac_list for item in elem]
vaccines = set(vaccines)
vaccines = list(vaccines)
vaccines


# In[28]:


#Now, I want to add a column with True/False for each vaccine, and only keep the row with the most recent information for each country.
#adding a column with True/False for each vaccine
for vaccin in vaccines:
    country[vaccin] = np.where(country['vaccines'].str.contains(vaccin), True, False)

country = country.sort_values(by = ['country', 'date'], ascending = [True, False])
country_latest = country.drop_duplicates(subset = "country", keep = "first")

#head of selected columns only
country_latest.iloc[:, np.r_[0,12, 15:len(country_latest.columns)]].head()


# # Choropleth Maps

# ## Worldwide usage maps by vaccine

# In[29]:


def plot_vaccin(color, vaccin):
    fig = px.choropleth(country_latest, locations="iso_code",
                        color=vaccin,
                        hover_name="country",
                        color_discrete_map={True: color, False: 'lightgrey'})

    layout = go.Layout(
        title=go.layout.Title(
            text= f"<b>Countries using {vaccin} vaccin</b>",
            x=0.5
        ),
        showlegend=False,
        font=dict(size=14),
        width = 750,
        height = 350,
        margin=dict(l=0,r=0,b=0,t=30)
    )

    fig.update_layout(layout)

    fig.show()


# In[30]:


plot_vaccin('red', 'Pfizer')


# In[31]:


plot_vaccin('green', "Moderna")


# In[32]:


plot_vaccin('brown', "AstraZeneca")


# In[33]:


plot_vaccin('orange', "Johnson&Johnson")


# In[34]:


plot_vaccin('blue', "Chinese")


# In[35]:


plot_vaccin('yellow', "Russian")


# In[36]:


plot_vaccin('magenta', "Indian")


# In[37]:


plot_vaccin('goldenrod', "Cuban")


# In[38]:


plot_vaccin('darkblue', "Kazachstan")


# # Worldwide map plotting the number of vaccines used by country

# In[39]:


#As you can see, many countries use only one or two different vaccines.
country_latest['Vaccins_used']= country_latest.iloc[:, -9:].sum(axis=1)
country_latest.Vaccins_used.value_counts()


# In[40]:


fig = px.choropleth(country_latest, locations="iso_code",
                    color='Vaccins_used',
                    hover_data= ["country", "vaccines"])

layout = go.Layout(
    title=go.layout.Title(
        text= f"<b>Number of different vaccines used by country</b>",
        x=0.5
    ),
    font=dict(size=14),
    width = 750,
    height = 350,
    margin=dict(l=0,r=0,b=0,t=30)
)

fig.update_layout(layout)

fig.show()


# In[ ]:





# In[ ]:




