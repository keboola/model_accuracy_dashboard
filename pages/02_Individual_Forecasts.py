import streamlit as st
from src.settings import ACCURACY_MONITORING_MEALS_TAB, ACCURACY_MONITORING_TAB, ACTUALS_NONAGG_TAB
from src.graphs import preprocess_data, create_series_plot_new
from src.graphs import filter_by_date
from src.helpers import read_df, calculate_categories
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page

if 'authentication_status' not in st.session_state:
    switch_page("login")

if st.session_state["authentication_status"]:
    
    df_meals = read_df(ACCURACY_MONITORING_MEALS_TAB, date_col=["approximate_timestamp"])
    df_accuracy = read_df(ACCURACY_MONITORING_TAB, date_col=["ds"])
    df_actuals = read_df(ACTUALS_NONAGG_TAB, date_col=["ds"])
    cat1, cat2, cat3 = calculate_categories(df_meals)
    
    with st.sidebar:
        category_type = st.selectbox("Category Type", cat1)
        outlet_type = st.selectbox("Outlet Type", cat2)
        outlet_number = st.selectbox("Outlet Number", cat3)
        category_selected = '~'.join([category_type, outlet_type, outlet_number])
    
    #meals_preprocessed = preprocess_data(df_meals, category_selected)
    accu_preprocessed = preprocess_data(df_accuracy, category_selected, time_col='ds')
    #actuals_preprocessed = preprocess_data(df_actuals, category_selected, time_col='ds', freq='15min')
    with st.sidebar:
        sc1, sc2 = st.columns(2)
        with sc1:
            start_date = st.date_input("Start Date", 
                                        value=accu_preprocessed.dt.min().date(),
                                        min_value=accu_preprocessed.dt.min().date(), 
                                        max_value=accu_preprocessed.dt.max().date()
                                        )
        with sc2:
            end_date = st.date_input("End Date", 
                                        value=accu_preprocessed.dt.max().date(),
                                        min_value=start_date, 
                                        max_value=accu_preprocessed.dt.max().date())

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)     
    #meals_preprocessed_filtered = filter_by_date(meals_preprocessed, start_date, end_date)
    accu_preprocessed_filtered = filter_by_date(accu_preprocessed, start_date, end_date)
    #actuals_preprocesses_filtered = filter_by_date(actuals_preprocessed, start_date, end_date)   
    
    sales_lunch_actual = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='lunch'].metric_actual.sum()
    sales_lunch_forecast_prophet = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='lunch'].metric_forecast.sum()
    sales_lunch_forecast_lgbm = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='lunch'].metric_forecast_lgbm.sum()
    sales_lunch_forecast_rf = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='lunch'].metric_forecast_rf.sum()

    lunch_pcnt_err_prophet = 100* np.abs(sales_lunch_forecast_prophet - sales_lunch_actual)/sales_lunch_actual
    lunch_pcnt_err_lgbm = 100* np.abs(sales_lunch_forecast_lgbm - sales_lunch_actual)/sales_lunch_actual
    lunch_pcnt_err_rf = 100* np.abs(sales_lunch_forecast_rf - sales_lunch_actual)/sales_lunch_actual

    sales_dinner_actual = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='dinner'].metric_actual.sum()
    sales_dinner_forecast_prophet = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='dinner'].metric_forecast.sum()
    sales_dinner_forecast_lgbm = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='dinner'].metric_forecast_lgbm.sum()
    sales_dinner_forecast_rf = accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category=='dinner'].metric_forecast_rf.sum()

    dinner_pcnt_err_prophet = 100* np.abs(sales_dinner_forecast_prophet - sales_dinner_actual)/sales_dinner_actual
    dinner_pcnt_err_lgbm = 100* np.abs(sales_dinner_forecast_lgbm - sales_dinner_actual)/sales_dinner_actual
    dinner_pcnt_err_rf = 100* np.abs(sales_dinner_forecast_rf - sales_dinner_actual)/sales_dinner_actual



    #if meals_preprocessed_filtered.empty:
    #    st.warning("No data for available for the selection.")
    #    st.stop()
    if accu_preprocessed_filtered.empty:
        st.warning("No data for available for the selection.")
        st.stop()

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Average error over lunch periods:")
            
            col11, col12, col13 = st.columns(3)
            with col11:
                st.metric("Prophet", f"{lunch_pcnt_err_prophet:.2f} %", f"{15 - lunch_pcnt_err_prophet:.2f} %")
            with col12:
                st.metric("LightGBM", f"{lunch_pcnt_err_lgbm:.2f} %", f"{15 - lunch_pcnt_err_lgbm:.2f} %")
            with col13:
                st.metric("Random Forest", f"{lunch_pcnt_err_rf:.2f} %", f"{15 - lunch_pcnt_err_rf:.2f} %")
            
        with col2:
            st.markdown("### Average error over dinner periods:")
            
            col21, col22, col23 = st.columns(3)
            with col21:
                st.metric("Prophet", f"{dinner_pcnt_err_prophet:.2f} %", f"{15 - dinner_pcnt_err_prophet:.2f} %")
            with col22:
                st.metric("LightGBM", f"{dinner_pcnt_err_lgbm:.2f} %", f"{15 - dinner_pcnt_err_lgbm:.2f} %")
            with col23:
                st.metric("Random Forest", f"{dinner_pcnt_err_rf:.2f} %", f"{15 - dinner_pcnt_err_rf:.2f} %")

            #st.metric("Prophet: Average error (%) over dinner periods:", f"{dinner_pcnt_err:.2f}", f"{15 - dinner_pcnt_err:.2f}")

    col1, col2 = st.columns(2)
    #with col1:
    #figure, raw_data = st.tabs(["figure", "raw_data"])
    
    
    #with figure:
        #st.dataframe(accu_preprocessed_filtered)
        #st.dataframe(accu_preprocessed)
    fig0 = create_series_plot_new(accu_preprocessed_filtered)
    st.plotly_chart(fig0, use_container_width=True, theme="streamlit")
    
    with st.sidebar:
        with st.form("my_form"):
            selectbox = st.selectbox("Select default model", ["Prophet", "LightGBM", "Random Forest"])
            
            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.warning("Not implemented yet. TODO: Update default model in Keboola")

    # with figure:
    #     fig1 = create_series_plot_meals(meals_preprocessed_filtered, actuals_preprocesses_filtered)
    #     st.plotly_chart(fig1, use_container_width=True)
    # with raw_data:
    #     st.dataframe(meals_preprocessed_filtered)
    # #with col2:
    # figure, raw_data = st.tabs(["figure", "raw_data"])
    # with figure:
    #     fig2 = create_series_plot_basic(accu_preprocessed_filtered, actuals_preprocesses_filtered)
    #     st.plotly_chart(fig2, use_container_width=True)
    # with raw_data:
    #     st.dataframe(accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category!=0])
            
    
    
    
    
    