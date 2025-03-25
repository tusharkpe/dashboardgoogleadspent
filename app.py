import streamlit as st
import pandas as pd
from datetime import datetime

# Load the datasets
campaign_file = "Campaign performance (1).csv"
ad_exchange_file = "(Mar 1, 2025 - Mar 23, 2025).csv"

def load_data():
    campaign_df = pd.read_csv(campaign_file)
    ad_exchange_df = pd.read_csv(ad_exchange_file)
    
    # Select relevant columns
    campaign_df = campaign_df[['Day', 'Country/Territory (Matched)', 'Conversions', 'Cost']]
    ad_exchange_df = ad_exchange_df[['Date', 'Country', 'Ad Exchange revenue ($)']]
    
    # Rename columns for consistency
    campaign_df.columns = ['Date', 'Country', 'Conversions', 'Spent']
    ad_exchange_df.columns = ['Date', 'Country', 'Ad Exchange revenue ($)']
    
    # Convert Date to datetime format
    campaign_df['Date'] = pd.to_datetime(campaign_df['Date'])
    ad_exchange_df['Date'] = pd.to_datetime(ad_exchange_df['Date'])
    
    # Merge both datasets on Date and Country
    merged_df = pd.merge(campaign_df, ad_exchange_df, on=['Date', 'Country'], how='left')
    
    # Calculate new columns
    merged_df['GST'] = merged_df['Spent'] * 0.18
    merged_df['Total Spent'] = merged_df['Spent'] + merged_df['GST']
    merged_df['Ad Exchange revenue ($) (INR)'] = merged_df['Ad Exchange revenue ($)'] * 87
    merged_df['Loss/Profit'] = merged_df['Ad Exchange revenue ($) (INR)'] - merged_df['Total Spent']
    
    return merged_df

data = load_data()

# Streamlit UI
st.title("Campaign Performance Dashboard")

# Date Range filter
date_range = st.date_input("Select Date Range", [datetime.today().date(), datetime.today().date()])

if len(date_range) != 2:
    st.error("Please select a valid start and end date.")
else:
    start_date, end_date = date_range
    
    # Country dropdown
    country_options = ['All Countries'] + list(data['Country'].unique())
    country = st.selectbox("Select Country", options=country_options)
    
    # Filter data by date range
    data_filtered = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]
    
    if country != 'All Countries':
        data_filtered = data_filtered[data_filtered['Country'] == country]
    
    # Ensure only one row total per day
    data_grouped = data_filtered.groupby('Date', as_index=False).sum()
    
    # Remove 'Country' column if it exists
    if 'Country' in data_grouped.columns:
        data_grouped = data_grouped.drop(columns=['Country'])
    columns_to_remove = ['Country', 'Ad Exchange revenue ($)']
    data_grouped = data_grouped.drop(columns=[col for col in columns_to_remove if col in data_grouped.columns])
    # Display data
    st.write("### Filtered Data")
    st.dataframe(data_grouped)
    
    # Summary Metrics
    st.write("### Summary Metrics")

    # Use CSS to adjust font size
    st.markdown(
        """
        <style>
        .metric-container {
            font-size: 16px !important;
        }
        .metric-value {
            font-size: 24px !important;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-container">Total Conversions</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{data_grouped["Conversions"].sum():,.0f}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-container">Total Spent</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">${data_grouped["Total Spent"].sum():,.2f}</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-container">Total Ad Exchange revenue ($) (INR)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">₹{data_grouped["Ad Exchange revenue ($) (INR)"].sum():,.2f}</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-container">Total Loss/Profit</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">₹{data_grouped["Loss/Profit"].sum():,.2f}</div>', unsafe_allow_html=True)

    # Download filtered data
    csv = data_grouped.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data as CSV", data=csv, file_name="filtered_data.csv", mime='text/csv')
