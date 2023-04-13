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
MEALS_TABLE = 'out.c-accuracy_monitoring.accuracy_monitoring_meals'