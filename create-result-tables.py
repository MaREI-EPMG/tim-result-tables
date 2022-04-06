#!/usr/bin/env python
# coding: utf-8

# # Create Result Tables

# In[1]:


import pathlib
import json
import pandas as pd
from tkinter import filedialog
from tkinter import Tk
from timeslib.misc import read_data_csv


# ### Specify input folder

# In[2]:


root=Tk()
input_folder = pathlib.Path(filedialog.askdirectory(title="Select input folder..."), parent=root, master=root)
root.destroy()


# ### Specify output folder

# In[3]:


root=Tk()
output_folder = pathlib.Path(filedialog.askdirectory(title="Select output folder..."), parent=root, master=root)
root.destroy()


# ### Load table info

# In[4]:


with open("./tim-tables-info/table_info.json", "r") as file:
    table_info = json.load(file)


# In[ ]:


# get list of all input data files with a certain name extension
path_list = sorted(input_folder.rglob("*.csv"))
print(
    "Found {} csv files.\n".format(len(path_list)),
    "\n".join("{}".format(k) for k in path_list),
    sep="",
)


# ### Read csv data into a dataframe

# In[6]:


# Create an empty DataFrame
data = pd.DataFrame()
# Read data into the dataframe
for a_table in table_info.keys():
    for a_table_rule in table_info[a_table].keys():
        file_path = input_folder/(a_table_rule + ".csv")
        if file_path.exists():
            df = read_data_csv(file_path,
                               {a_table_rule: table_info[a_table][a_table_rule]})
            if df is not None:
                df["tableName"] = a_table
                data = pd.concat([data, df], ignore_index=True)

assert len(data.index), "The dataframe is empty. No data has been read."

data = data.groupby([i for i in data.columns if not i == "total"]).agg("sum")
data = data.reset_index()


# ### Print results to excel files

# In[7]:


for aScenario in data["scenario"].unique():
        temp_df = (
            data[
                (data["scenario"] == aScenario)
            ]
            .drop(columns=["scenario"])
            .pivot(index=["tableName", "serieName"], columns="year", values="total")
        )
        temp_df.fillna(value=0, inplace=True)
        temp_df.index = [temp_df.index.map("{0[0]} [{0[1]}]".format)]
        temp_df.to_excel(output_folder/(aScenario + ".xlsx"))
