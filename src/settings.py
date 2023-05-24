#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 14:21:10 2023

@author: ondrejsvoboda
"""

import streamlit as st
from kbcstorage.client import Client

# credentials
KEBOOLA_STACK = st.secrets["kbc_url"]
KEBOOLA_TOKEN = st.secrets["kbc_token"]
keboola_client = Client(KEBOOLA_STACK, KEBOOLA_TOKEN)

# tables 
ACCURACY_MONITORING_MEALS_TAB = 'out.c-accuracy_monitoring.accuracy_monitoring_meals'
ACCURACY_MONITORING_TAB = 'out.c-accuracy_monitoring.accuracy_monitoring'
ACTUALS_NONAGG_TAB = 'out.c-accuracy_monitoring.actuals_nonagg'
STREAMLIT_BUCKET_ID = 'out.c-streamlit_out'
DEFAULT_MODEL_TAB = 'out.c-streamlit_out.default_model'

# color coding

colors = {}
colors["Prophet"] = "blue"
colors["Random Forest"] = "red"
colors["LightGBM"] = "green"