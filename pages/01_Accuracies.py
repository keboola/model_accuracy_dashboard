#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 15:01:11 2023

@author: ondrejsvoboda
"""

import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from src.helpers import read_df, create_summary_table
from src.settings import ACCURACY_MONITORING_TAB

if 'authentication_status' not in st.session_state:
    switch_page("login")

df_accuracy = read_df(ACCURACY_MONITORING_TAB, date_col=["ds"])

#st.session_state["df_accuracy"]=df_accuracy

with st.sidebar:
    sc1, sc2 = st.columns(2)
    with sc1:
        start_date = st.date_input("Start Date", 
                                    value=df_accuracy.ds.min().date(),
                                    min_value=df_accuracy.ds.min().date(), 
                                    max_value=df_accuracy.ds.max().date()
                                    )
    with sc2:
        end_date = st.date_input("End Date", 
                                    value=df_accuracy.ds.max().date(),
                                    min_value=start_date, 
                                    max_value=df_accuracy.ds.max().date())


summary_df = create_summary_table(df_accuracy, str(start_date), str(end_date))

def color_negative_red(value):
  """
  Colors elements in a dateframe
  green if positive and red if
  negative. Does not color NaN
  values.
  """

  if value < 15:
    color = 'green'
  elif value > 0:
    color = 'red'
  else:
    color = 'black'

  return 'color: %s' % color



st.markdown("### Average percentage error over defined period")

t1, t2 = st.tabs(["Summary", "Detailed"])

cols = ["prophet_mean", "lgbm_mean", "rf_mean"]

with t1:
    st.dataframe(summary_df[cols].style.applymap(color_negative_red))
with t2:
    cols = [c for c in summary_df.columns if not c.endswith("_mean")]
    st.dataframe(summary_df[cols].style.applymap(color_negative_red))






