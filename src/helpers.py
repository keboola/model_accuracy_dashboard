#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:12:30 2023

@author: ondrejsvoboda
"""

import streamlit as st
from src.settings import keboola_client, STREAMLIT_BUCKET_ID
import pandas as pd
import numpy as np
import datetime
import csv

def parse_credentials():
    """
    The method takes credentials from streamlit secret and converts
    these into a dictionary compatible with streamlit authenticator
    expected composition of secret variable
    credentials_usernames_USERNAME_VARIABLE
    
    eg
    
    credentials_usernames_ondra_email = 'ondrej.svoboda@keboola.com'
    credentials_usernames_ondra_name = 'Ondřej Svoboda'
    credentials_usernames_ondra_password = 'xxx'
    this would be converted into 
    
    {"credentials":{
        "usernames":{
            "ondra":{
                "email": 'ondrej.svoboda@keboola.com',
                "name": 'Ondřej Svoboda', 
                "password": 'xxx'
                }
            }
        }}
    Returns
    -------
    config_dict - dictionary containing information about credentials formatted
    for stauth
    
    NOTE
    ----
    advanced features of stauth are not currently implemented beyond the simplest
    use. For instance, no preauthorized users or passwords expiry
    """
    config_dict = {}
    
    # 1. check the longest inner subscription
    
    # at this point, I do not check for preauthorized or cookies
    for key in st.secrets:
        creds_dict = config_dict.get("credentials", dict())
        username_dict = creds_dict.get("usernames", dict())    
        username = key.split('_')[-2]
        key_end = key.split('_')[-1]
        user_dict =  username_dict.get(username, dict())
        user_dict[key_end] = st.secrets[key]
        username_dict[username] = user_dict
        creds_dict["usernames"] = username_dict
        config_dict["credentials"] = creds_dict
    
    config_dict["cookie"] = {'expiry_days':0,
                             'key':"random_signature_key",
                             'name':"random_cookie_name"}
    
    config_dict["preauthorized"] = {'emails':["melsby@gmail.com"]}
    
    return config_dict

def MAPE(Y_actual,Y_Predicted):
    """
    Calculates mean average percentage error

    Parameters
    ----------
    Y_actual : 
        array of actuals.
    Y_Predicted : 
        array of forcasted data

    Returns
    -------
    mape : float
        returns the value of the metric.

    """
    mape = np.mean(np.abs((Y_actual - Y_Predicted)/Y_actual))*100
    return mape    

@st.cache_data
def read_df(table_id, index_col=None, date_col=None):
    """
    The function reads the table contents from keboola storage using
    Keboola SAPI client, see 
    https://github.com/keboola/sapi-python-client
    

    Parameters
    ----------
    table_id : table id of keboola table 
        DESCRIPTION.
    index_col : srting, optional
        possible index column. The default is None.
    date_col : list, optional
        list of date columns. The default is None.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    keboola_client.tables.export_to_file(table_id, '.')
    table_name = table_id.split(".")[-1]
    return pd.read_csv(table_name, index_col=index_col, parse_dates=date_col)

@st.cache_data
def calculate_categories(original_dataframe):
    split_series = original_dataframe.category.str.split('~', expand=True)
    cat1 = split_series[0].unique()
    cat2 = split_series[1].unique()
    cat3 = split_series[2].unique()
    return cat1, cat2, cat3

@st.cache_data
def group_accuracy_df(dataframe):
    dfgrouped = dataframe.groupby(["date", "category", "meal_category"])[["metric_actual", "metric_forecast", "metric_forecast_lgbm", "metric_forecast_rf"]].sum().reset_index()
    dfgrouped["APE_prophet"]= np.abs((dfgrouped["metric_actual"] - dfgrouped["metric_forecast"])/dfgrouped["metric_actual"])
    dfgrouped["APE_lgbm"]= np.abs((dfgrouped["metric_actual"] - dfgrouped["metric_forecast_lgbm"])/dfgrouped["metric_actual"])
    dfgrouped["APE_rf"]= np.abs((dfgrouped["metric_actual"] - dfgrouped["metric_forecast_rf"])/dfgrouped["metric_actual"])
    return dfgrouped

def create_summary_table(dataframe, default_model, start_date, end_date):
    dfgrouped = group_accuracy_df(dataframe)
    df_filtered = dfgrouped.loc[(dfgrouped.date>=start_date) & (dfgrouped.date<=end_date)]

    cols = ["metric_actual", 
        "APE_prophet", 
        "APE_lgbm", 
        "APE_rf"
       ]

    dff_grouped = df_filtered.groupby(["category", "meal_category"])[cols]
    summary_df = dff_grouped.agg(
        mape_prophet = pd.NamedAgg(column="APE_prophet", aggfunc="mean"),
        mape_lgbm = pd.NamedAgg(column="APE_lgbm", aggfunc="mean"),
        mape_rf = pd.NamedAgg(column="APE_rf", aggfunc="mean"),
        ).reset_index()
    
    summary_df["mape_prophet"] = 100 * summary_df["mape_prophet"]
    summary_df["mape_lgbm"] = 100 * summary_df["mape_lgbm"]
    summary_df["mape_rf"] = 100 * summary_df["mape_rf"]
    
    summary_df.pivot(columns=["meal_category"], index=["category"])
    summary_pivot_df = summary_df.pivot_table(columns=["meal_category"], index=["category"])
    colnames = ['_'.join([c1, c2]) for c1, c2 in summary_df.pivot_table(columns=["meal_category"], index=["category"]).columns]
    summary_pivot_df.columns=colnames
    summary_pivot_df["prophet_mean"] = (summary_pivot_df["mape_prophet_lunch"] + summary_pivot_df["mape_prophet_dinner"]) / 2
    summary_pivot_df["lgbm_mean"] = (summary_pivot_df["mape_lgbm_lunch"] + summary_pivot_df["mape_lgbm_dinner"]) / 2
    summary_pivot_df["rf_mean"] = (summary_pivot_df["mape_rf_lunch"] + summary_pivot_df["mape_rf_dinner"]) / 2
    
    summary_pivot_df.sort_values(by="prophet_mean", inplace=True)
    summary_pivot_df.reset_index(inplace=True)
    summary_pivot_df = pd.merge(summary_pivot_df, default_model, on="category")
    summary_pivot_df.set_index("category", inplace=True)

    return summary_pivot_df

def create_or_update_table(table_name,
        keboola_client=keboola_client,
        bucket_id=STREAMLIT_BUCKET_ID,
        file_path='.default_model.csv',
        is_incremental=True, 
        delimiter=',',
        enclosure='"', 
        escaped_by='', 
        columns=["category"],
        without_headers=False):
    """
    The function creates or incrementally updates the mapping table. 
    Mapping table should be keyed by hash(config_id+class)

    Parameters
    ----------
    table_name : TYPE
        DESCRIPTION.
    keboola_client : TYPE, optional
        DESCRIPTION. The default is keboola_client.
    bucket_id : TYPE, optional
        DESCRIPTION. The default is 'out.c-create_configs'.
    file_path : TYPE, optional
        DESCRIPTION. The default is '.mapping.csv'.
    # define primary key        is_incremental : TYPE, optional
        DESCRIPTION. The default is False.
    delimiter : TYPE, optional
        DESCRIPTION. The default is ','.
    enclosure : TYPE, optional
        DESCRIPTION. The default is '"'.
    escaped_by : TYPE, optional
        DESCRIPTION. The default is ''.
    columns : TYPE, optional
        DESCRIPTION. The default is None.
    without_headers : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    # check whether a table in the bucket exists. If so, retrieve its table_id
    try:
        try:
            tables = keboola_client.tables.list()

        except Exception as e:
            return str(e)
        # there will be 0 or 1 hit
        table_def = list(filter(lambda x: x['bucket']['id']==bucket_id and x['name']==table_name, tables))
        if table_def:
            table_id = table_def[0]['id']
            # table already exists --> load
            try:
                _= keboola_client.tables.load(table_id=table_id,
                                    file_path=file_path,
                                    is_incremental=is_incremental, 
                                    delimiter=delimiter,
                                    enclosure=enclosure, 
                                    escaped_by=escaped_by,
                                    columns=columns,
                                    without_headers=without_headers) 
                return True, f"{table_name} table has been updated."
            except Exception as e:
                return False, str(e)    
        else:
            # table does not exist --> create
            try:
                return True, keboola_client.tables.create(name=table_name,
                                    bucket_id=bucket_id,
                                    file_path=file_path,
                                    primary_key=columns) + " table has been successfully created!!"
            except Exception as e:
                return False, str(e)   
    except Exception as e:
        return False, str(e)             



def update_default_model(model_name, category, file='.default_model.csv'):
    """
    

    Parameters
    ----------
    model_name : string
        model name coming from selectbox.
    category : string
        category as defined in the project.

    Returns
    -------
    None.

    """
    timestamp = datetime.datetime.now()

    update = {
        "category":category,
        "default_model":model_name,
        "updated_timestamp":timestamp
        }
    
    field_names = update.keys()
    with open(file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_names)
        writer.writeheader()
        writer.writerows([update])
    
    return None






