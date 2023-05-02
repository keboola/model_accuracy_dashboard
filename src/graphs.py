#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 14:25:26 2023

@author: ondrejsvoboda
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import datetime

@st.cache_data
def preprocess_data(original_dataframe:pd.DataFrame, category, time_col='approximate_timestamp'):
    
    FILTER = (original_dataframe.category==category)
    #st.dataframe(original_dataframe)
    df = original_dataframe.copy().loc[FILTER]
    dates_filled = pd.date_range(start=df[time_col].min(), end=df[time_col].max(), freq='1H')
    df.reset_index(drop=True, inplace=True)
    df.set_index(time_col, inplace=True)
    df.sort_index(inplace=True)
    df = df.reindex(dates_filled, fill_value=0)
    df.reset_index(inplace=True)
    df.rename(columns={"index":"dt"}, inplace=True)
    #df.sort_values(by=time_col, inplace=True)
    #df.rename(columns={time_col:"dt"}, inplace=True)
    return df

def filter_by_date(dataframe:pd.DataFrame, date_start:datetime.date, date_end:datetime.date):
    return dataframe.loc[(dataframe.dt >= date_start) & (dataframe.dt <= date_end)]
    

def create_series_plot_meals(dataframe:pd.DataFrame()):
    
    fig = px.scatter(x=dataframe.loc[dataframe.records_count!=0]['dt'], 
                     y=dataframe.loc[dataframe.records_count!=0]['sales_per_meal_forecasts'], 
                     color=dataframe.loc[dataframe.records_count!=0]['PH_good'], width=1200, height=800,
                    title="Actuals vs Forecasts, parts of day, data points labeled by aggregated sales and 1O % difference",
                     color_discrete_map= {0: 'red',
                                          1: 'green'
                                          })
    fig.add_scatter(x=dataframe['dt'],
                    y=dataframe['sales_per_meal_actuals'], name='Actual data', mode='lines', line=dict(color="grey"))
    fig.add_scatter(x=dataframe['dt'], 
                    y=dataframe['sales_per_meal_forecasts'], name='Forecasted data', mode='lines', line=dict(color="blue"))
    fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey', griddash='dash')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey', griddash='dash')
    fig.update_layout( yaxis_range=[0.1,1.2*dataframe.sales_per_meal_actuals.max()],
                     plot_bgcolor='white'
                     )
    return fig

def create_series_plot_basic(dataframe:pd.DataFrame):
    fig = px.scatter(x=dataframe.loc[dataframe.forecast_label!=0]['dt'], 
                 y=dataframe.loc[dataframe.forecast_label!=0]['metric_forecast'], 
                 color=dataframe.loc[dataframe.forecast_label!=0]['forecast_label'], width=1200, height=800, 
                 title="Actuals vs Forecasts, data points labeled by comparing with standard deviation",
                 color_discrete_map= {'GOOD': 'green',
                                      'WARNING': 'orange',
                                      'BAD': 'red'
                                      })
    fig.add_scatter(x=dataframe['dt'], y=dataframe['metric_actual'], name='Actual data', mode='lines', line=dict(color="grey"))
    fig.add_scatter(x=dataframe['dt'], y=dataframe['metric_forecast'], name='Forecasted data', mode='lines', line=dict(color="blue"))
    fig.update_layout(yaxis_range=[0.1,1.2*dataframe.metric_actual.max()], 
                     #paper_bgcolor='rgba(0,0,0,0)', 
                     plot_bgcolor='white'
                     )
    fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey', griddash='dash')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey', griddash='dash')
    return fig