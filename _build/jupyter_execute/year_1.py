#!/usr/bin/env python
# coding: utf-8

# In[6]:


# sys, file and nav packages:
import datetime as dt

# math packages:
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.distributions.empirical_distribution import ECDF

# charting:
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# home brew utitilties
# import resources.chart_kwargs as ck
import resources.sr_ut as sut

# images and display
from IPython.display import Markdown as md
from IPython.display import Image


# # Cordova Creek 
# 
# Cordova Creek was orginally named Clifton drain which is/was a concrete channel established for evacuating runoff to the American River. The Cordova Creek Naturalization Project (CCNP) started in early 2016 with the goal of restoring natural form and function to a portion of the channelized stream. The naturalized waterway, which provides both critical habitat and water quality benefits, was renamed Cordova Creek. 
# 
# The River Bend Park Area at the time the plan called for the restoration of Cordova Creek to create a riparian corridor that would filter urban runoff and serve as a buffer between the nature study area to the west and the developed recreational uses to the east. It also calls for bringing together native plant nursery, organic farming operations and riparian habitat to enhance interpretation opportunities.
# 
# ## Monitoring aquatic litter
# 
# In 2015 we began a project with a goal to quantify the debris flowing to the American River and one of its tributaries: Cordova Creek. The surveys followed the protocol described in _The Guide for Monitoriing litter on European seas_ :
# 
# 1. Take pictures of location, including visible debris present
# 2. Note location, date, length of survey area
# 3. Remove all visible debris items from within the survey perimeter using standard retrieval methods/equipment
# 4. Place all debris items on a tarp
# 5. Count and photograph the array of items
# 6. Enter data in the survey app
# 7. Once all items have been documented dispose, or recycle
# 
# Surveys were conducted weekly on Wednesday morninging and anounced via social media in advance. The surveyor maintained a blog with an entry for most surveys [hammerdirt at riverbend](https://hammerdirtriverbend.blogspot.com). 

# In[7]:


Image("resources/images/map.png")


# ## Survey Results 

# There were 56 surveys completed between November 2015 and April 2017 (Figure 1). The median survey results was 5 pieces of trash  per meter (pcs/m), the average was 6 pcs/m (Table 1). Plastic comprised 80% of the inventory the next closest were metal and paper $\approxeq$ 7% (Table 2).

# _**Below:** Left Figure one total survey resulsts_

# In[2]:


# using the server data
server_data = pd.read_csv('resources/the_data.csv')
unit_label = "pcs_m"

# drop unnamed column:
def drop_this_column(data, column='Unnamed: 0'):
    if column in data.columns:
        data.drop(column, inplace=True, axis=1)
for datas in [server_data]:
    drop_this_column(datas)

fd = server_data[server_data.location == 'cordova-creek'].copy()
fd["loc_date"] = list(zip(fd["location"], fd["date"]))
fd["date"] = pd.to_datetime(fd["date"])
fd["month"] = fd["date"].dt.month

# number of samples
nsamps = fd.loc_date.unique()

# total quantity
qty = fd.quantity.sum()

# avg qty
avg_qty = fd.groupby("loc_date").quantity.sum().mean()

# average and median pcs/m
avg_pcsm = fd.groupby("loc_date").pcs_m.sum().mean()
md_pcsm = fd.groupby("loc_date").pcs_m.sum().median()

# daily totals
dts_date = fd.groupby(["loc_date", "date"], as_index=False).pcs_m.sum()

# months locator, can be confusing
# https://matplotlib.org/stable/api/dates_api.html
# months = mdates.MonthLocator(interval=1)
months_fmt = mdates.DateFormatter("%b")
days = mdates.DayLocator(interval=7)
sns.set_style("whitegrid")

fig, axs = plt.subplots(1,2, figsize=(10,5))

# the survey totals by day
ax = axs[0]

# feature surveys
sns.scatterplot(x=dts_date["date"], y=dts_date["pcs_m"], label="Survey pieces of trash per meter", color="black", alpha=0.4,  ax=ax)

ax.set_ylabel("pieces of trash per meter")
ax.set_xlabel("")
ax.xaxis.set_minor_locator(days)
ax.xaxis.set_major_formatter(months_fmt)
ax.legend()

# the cumlative distributions:
axtwo = axs[1]

# the feature of interest
feature_ecd = ECDF(dts_date[unit_label].values)    
sns.lineplot(x=feature_ecd.x, y=feature_ecd.y, color="darkblue", ax=axtwo, label="Cumulative ditribution")

axtwo.set_xlabel("Pieces of trash per meter") 
axtwo.set_ylabel("Ratio of samples")

plt.tight_layout()
plt.show()


# _**Below:** Right Table 1 sunmary of survey totals. Left Table 2 material type and totals._

# In[3]:


# get the basic statistics from pd.describe
cs = dts_date[unit_label].describe().round(2)

# change the names 
csx = sut.change_series_index_labels(cs, sut.create_summary_table_index(unit_label, lang="EN"))

combined_summary = sut.fmt_combined_summary(csx, nf=[])

# map code description
dfCodes = pd.read_csv("resources/codes_with_group_names_2015.csv")

# common aggregations
code_map = dfCodes[["code", "description"]].set_index("code")
material_map = dfCodes[["code", "material"]].set_index("code")

agg_pcs_quantity = {unit_label:"sum", "quantity":"sum"}
agg_pcs_median = {unit_label:"median", "quantity":"sum"}
 
fd["material"] = fd.code.map(lambda x: material_map.loc[x][0])
mattotals = fd.groupby('material', as_index=False).quantity.sum()
mattotals["% of total"] = ((mattotals.quantity/mattotals.quantity.sum())*100).round(1)
mat_data = mattotals[["material", "quantity", "% of total"]].copy()

# applly new column names for printing
cols_to_use = {"material":"Material","quantity":"Quantity", "% of total":"% of total"}

# make tables
fig, axs = plt.subplots(1,2, figsize=(8,6))

# summary table
# names for the table columns
a_col = ["name", "total"]

axone = axs[0]
sut.hide_spines_ticks_grids(axone)

table_two = sut.make_a_table(axone, combined_summary,  colLabels=a_col, colWidths=[.5,.25,.25],  bbox=[0,0,1,1], **{"loc":"lower center"})
table_two.get_celld()[(0,0)].get_text().set_text(" ")

# material table
axtwo = axs[1]
axtwo.set_xlabel(" ")
sut.hide_spines_ticks_grids(axtwo)

table_three = sut.make_a_table(axtwo, mat_data.values,  colLabels=mat_data.columns, colWidths=[.4, .3,.3],  bbox=[0,0,1,1], **{"loc":"lower center"})
# table_three.get_celld()[(0,0)].get_text().set_text(" ")

plt.tight_layout()
plt.subplots_adjust(wspace=0.2)
plt.show()


# ## The most common objects
# 
# Foam polystyrene was the most by quantity however snack wrappers were found at a greater percentage of the surveys. Fractured plastics and polystyrene were found more often than cigarettes  (Table 3),
# 
# _**Below:** The twenty most common items from 2015-2017_

# In[4]:


# the top 20 codes
codes = fd.groupby(['loc_date','code'], as_index=False).agg({'pcs_m':'sum', 'quantity':'sum'})
codes["fail"] = codes.quantity > 0
codes = codes.groupby("code").agg({'quantity':'sum', 'pcs_m':'median', 'fail':'sum'})
codes["fail rate"] = ((codes.fail/56)*100).round(1)
codes["pcs_m"] = codes["pcs_m"].round(2)
top_20 = codes.sort_values(by="quantity", ascending=False)[:20]
top_20 = top_20.reset_index()

# map code description
dfCodes = pd.read_csv("resources/codes_with_group_names_2015.csv")
code_map = dfCodes[["code", "description"]].set_index("code")

top_20["description"] = top_20.code.map(lambda x: code_map.loc[x][0])
table_vals = ["description", "quantity", "pcs_m", "fail rate"]

table_data = top_20[table_vals].copy()
table_data.rename(columns={"quantity":"Quantity", "pcs_m":"pcs/m"}, inplace=True)

# make table
data = table_data
colLabels = table_data.columns

fig, ax = plt.subplots(figsize=(len(colLabels)*3,len(data)*.7))

sut.hide_spines_ticks_grids(ax)
table_one = sut.make_a_table(ax, data.values, colLabels=colLabels, a_color="saddlebrown", colWidths=[.48, *[.13]*4])
table_one.get_celld()[(0,0)].get_text().set_text(" ")

plt.show()
plt.tight_layout()
plt.close()


# ## Discussion
# 
# The use of litter data gathered by observations to assess compliance with State Water Resources Control Board resolution 2015-2019 (SWRCB, 2015-0019) was considered by connely et all in 2016. In this study observations were taken from a moving vehichle throughout the city salinas.  The observations were considered using Bayesian uncertaintiy estimation to produce a geographic representation of the magnitude of the observations by some measureing unit. Recently different protocols were considered in the San Francisc bay to qauntify trash in recieveing waters. In the context of (SWRCB, 2015-0019) the presence and the density of litter in recieveing waters is an essential element to understanding and mitigating the problem.
# 
# The goal of monitoring is to assess the changes over time, litter monitoring is one way to accmoplish that goal with respect to (SWRCB, 2015-0019). Litter data gathered by volunteers in Europe over one year was used to establish the current threshhold value of 15 pieces of trash per 100 meters for european beaches. Cordova Creek I (2015 - 2017) had a median value of 5.2 pieces/meter. It is likely that the CCNP had a beneficial effect on the transfer of trash to reciveing waters given that the  samples taken in January and February 2022 were both lower than the baseline in CCI.
# 
# 
# The final phase of CCNP (scheduled 2024-2025) is an opportunity to compare the changes over time in litter density from 2017 - 2022 in the context of the SWRCB, 2015-0019. Furthermore, it is an opportunity to measure beneficial(trash capture) effects of the (CCNP) project design of the confluence both before, and after final phase implementation.
# 
# 
# 
# 

# In[ ]:




