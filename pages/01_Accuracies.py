#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 15:01:11 2023

@author: ondrejsvoboda
"""

import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from src.helpers import read_df, create_summary_table
from src.settings import ACCURACY_MONITORING_TAB, DEFAULT_MODEL_TAB
import datetime

if 'authentication_status' not in st.session_state:
    switch_page("login")

df_accuracy = read_df(ACCURACY_MONITORING_TAB, date_col=["ds"])

if "default_model" not in st.session_state.keys():
    default_model = read_df(DEFAULT_MODEL_TAB)
    st.session_state["default_model"] = default_model
else:
    default_model = st.session_state["default_model"]


#default_model.drop(columns=["updated_timestamp"], inplace=True)

with st.sidebar:
    sc1, sc2 = st.columns(2)
    with sc1:
        if "start_date" in st.session_state:
            value = st.session_state["start_date"]
        else:
            value = df_accuracy.ds.min().date()
        start_date = st.date_input("Start Date", 
                                    value=value,
                                    min_value=df_accuracy.ds.min().date(), 
                                    max_value=df_accuracy.ds.max().date()
                                    )
        st.session_state["start_date"] = start_date
    with sc2:
        if "end_date" in st.session_state:
            value = st.session_state["end_date"]
        else:
            value = df_accuracy.ds.max().date()

        end_date = st.date_input("End Date", 
                                    value=value,
                                    min_value=start_date, 
                                    max_value=df_accuracy.ds.max().date()
                                    )

# we need to include the last date of selection
end_date = end_date + datetime.timedelta(days=1)
summary_df = create_summary_table(df_accuracy, default_model, str(start_date), str(end_date))

def color_negative_red(value):
  """
  Colors elements in a dateframe
  green if positive and red if
  negative. Does not color NaN
  values.
  """

  if float(value) < 15:
    color = 'green'
  elif (value) > 0:
    color = 'red'
  else:
    color = 'black'

  return 'color: %s' % color

st.markdown("### Mean Average Percentage Error (MAPE) over defined period")

t1, t2 = st.tabs(["Summary", "Detailed"])

cols = ["prophet_mean", "lgbm_mean", "rf_mean", "default_model"]

with t1:
    st.dataframe(summary_df[cols].style.applymap(color_negative_red, 
                                                 subset=["prophet_mean", "lgbm_mean", "rf_mean"]
                                                 ).format('{:.2f} %',
                                                          subset=["prophet_mean", "lgbm_mean", "rf_mean"]
                                                          ))

with t2:
    cols = [c for c in summary_df.columns if not c.endswith("_mean") and c!="updated_timestamp"]
    st.dataframe(summary_df[cols].style.applymap(color_negative_red,
                                                 subset = [c for c in cols if c!="default_model"]
                                                 ).format('{:.2f} %', 
                                                          subset=[c for c in cols if c!="default_model"]
                                                          ))






