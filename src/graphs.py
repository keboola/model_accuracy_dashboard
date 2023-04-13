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

def preprocess_data(original_dataframe:pd.DataFrame, category, time_since):
    
    FILTER = (original_dataframe.category==category) & (original_dataframe.approximate_timestamp>=str(time_since))

    df = original_dataframe.copy().loc[FILTER]
    dates_filled = pd.date_range(start=df.approximate_timestamp.min(), end=df.approximate_timestamp.max(), freq='1H')
    df.reset_index(drop=True, inplace=True)
    df.set_index("approximate_timestamp", inplace=True)
    df.sort_index(inplace=True)
    #st.dataframe(df)
    #st.write(df.index)
    df = df.reindex(dates_filled, fill_value=0)
    #st.write(df.index)

    #st.dataframe(df)

    df.reset_index(inplace=True)
    return df

def create_series_plot(dataframe:pd.DataFrame()):
    
    fig = px.scatter(x=dataframe['index'], 
                     y=dataframe['max_actual'], 
                     color=dataframe['10pcntRule'], width=1200, height=800,
                    title="Actuals vs Forecasts, parts of day, data points labeled by comparing with 1O % difference",
    
                     color_discrete_map= {0: 'red',
                                          1: 'green'
                                          })
    fig.add_scatter(x=dataframe['index'],
                    y=dataframe['max_actual'], name='Actual data', mode='lines', line=dict(color="grey"))
    fig.add_scatter(x=dataframe['index'], 
                    y=dataframe['max_forecast'], name='Forecasted data', mode='lines', line=dict(color="blue"))
    fig.update_traces(marker=dict(size=12,
                                  line=dict(width=2,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey', griddash='dash')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey', griddash='dash')
    fig.update_layout( yaxis_range=[0.1,1.2*dataframe.max_actual.max()],
                     plot_bgcolor='white'
                     )
    return fig