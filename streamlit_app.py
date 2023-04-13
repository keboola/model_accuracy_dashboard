import streamlit as st
import streamlit_authenticator as stauth
from src.helpers import parse_credentials, read_df, calculate_categories
from src.settings import ACCURACY_MONITORING_MEALS_TAB, ACCURACY_MONITORING_TAB
from src.graphs import preprocess_data, create_series_plot_meals, create_series_plot_basic
from src.graphs import filter_by_date
import pandas as pd

st.set_page_config(
    page_title="Model Dashboard",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

config_dict = parse_credentials()

authenticator = stauth.Authenticate(
    config_dict['credentials'],
    config_dict['cookie']['name'],
    config_dict['cookie']['key'],
    config_dict['cookie']['expiry_days'],
    config_dict['preauthorized']
)

with st.sidebar:
    st.title('Harri - Model Accuracy Dashboard')

    name, authentication_status, username = authenticator.login('Login', 'main')


if authentication_status:
    with st.sidebar:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
elif authentication_status == False:
    with st.sidebar:
        st.error('Username/password is incorrect')
elif authentication_status == None:
    with st.sidebar:
        st.warning('Please enter your username and password')

if authentication_status:
    
    df_meals = read_df(ACCURACY_MONITORING_MEALS_TAB, date_col=["approximate_timestamp"])
    df_accuracy = read_df(ACCURACY_MONITORING_TAB, date_col=["ds"])

    cat1, cat2, cat3 = calculate_categories(df_meals)
    
    with st.sidebar:
        #date = st.date_input("Date Since", datetime.date(2023, 3, 20))
        category_type = st.selectbox("Category Type", cat1)
        outlet_type = st.selectbox("Outlet Type", cat2)
        outlet_number = st.selectbox("Outlet Number", cat3)
        category_selected = '~'.join([category_type, outlet_type, outlet_number])
        
    meals_preprocessed = preprocess_data(df_meals, category_selected)
    accu_preprocessed = preprocess_data(df_accuracy, category_selected, time_col='ds')


    with st.sidebar:
        start_date, end_date = st.slider(
            "Select date range",
            value=(meals_preprocessed.dt.min().date(), meals_preprocessed.dt.max().date()), 
            format="MM/DD/YY"
            )
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)    
    meals_preprocessed_filtered = filter_by_date(meals_preprocessed, start_date, end_date)
    accu_preprocessed_filtered = filter_by_date(accu_preprocessed, start_date, end_date)
        
    col1, col2 = st.columns(2)
    with col1:
        figure, raw_data = st.tabs(["figure", "raw_data"])
        with figure:
            fig1 = create_series_plot_meals(meals_preprocessed_filtered)
            st.plotly_chart(fig1, use_container_width=True)
        with raw_data:
            st.dataframe(meals_preprocessed_filtered.loc[meals_preprocessed_filtered.meal_category!=0])
    with col2:
        figure, raw_data = st.tabs(["figure", "raw_data"])
        with figure:
            fig2 = create_series_plot_basic(accu_preprocessed_filtered)
            st.plotly_chart(fig2, use_container_width=True)
        with raw_data:
            st.dataframe(accu_preprocessed_filtered.loc[accu_preprocessed_filtered.meal_category!=0])
            
    
    
    
    
    