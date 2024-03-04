import streamlit as st
import pandas as pd
# import yfinance as yf
import datetime
import plotly.express as px

# Load data containing symbols and company names
data = pd.read_csv("EQUITY_L.csv")

# Extract stock symbols from the data
stock_symbols = data['SYMBOL'].tolist()

# Informative message about data availability
st.info("Dive deeper with this data! It provides minute-by-minute details for the past 30 days, giving you high-resolution insights.")

# Stock selection dropdown
stock_selected = st.sidebar.selectbox("Choose stock", stock_symbols)

# Concatenate with '.NS'
stock_symbol = f"{stock_selected}.NS"

# Default start date (today's date)
default_start_date = datetime.date.today()

# Date input widgets with HTML5 min attribute
selected_date = st.sidebar.date_input("Select a start date", default_start_date, datetime.date(1700, 1, 1))
end_date = st.sidebar.date_input("Select an end date", default_start_date)

# Time range selection
time_range_options = [None, '1D', '5D', '1M', '6M', '1Y', '5Y', 'MAX']
selected_time_range = st.sidebar.selectbox("Select time range", time_range_options)

# Download option selection (checkbox)
intraday_data = st.sidebar.checkbox("Download Intraday (Minute) Data")

# Calculate start and end dates based on selections
if selected_time_range:
    # Handle pre-defined time ranges
    if selected_time_range == '1D':
        start_date = selected_date
        end_date = selected_date  # No need to add a day here
    else:
        # Calculate start date based on selected time range
        if selected_time_range == '5D':
            start_date = end_date - datetime.timedelta(days=4)
        elif selected_time_range == '1M':
            start_date = end_date - datetime.timedelta(days=30)
        elif selected_time_range == '6M':
            start_date = end_date - datetime.timedelta(days=180)
        elif selected_time_range == '1Y':
            start_date = end_date - datetime.timedelta(days=365)
        elif selected_time_range == '5Y':
            start_date = end_date - datetime.timedelta(days=5*365)
        elif selected_time_range == 'MAX':
            start_date = datetime.date(1700, 1, 1)
else:
    start_date = selected_date
    # Fix for end date selection: Add one day only if it's different from start_date
    end_date = end_date if end_date == selected_date else end_date + datetime.timedelta(days=1)

# Download stock data
if intraday_data:
    # Download minute data for a single day even if user accidentally adds a day in end_date
    if start_date == end_date:
        # Try downloading minute data for the entire trading day
        start_time = datetime.datetime.combine(start_date, datetime.time(9, 15))  # Market open time
        end_time = datetime.datetime.combine(start_date, datetime.time(15, 30))  # Market close time (tentative)
        data = yf.download(stock_symbol, start=start_time, end=end_time, interval="1m")

        # Check if data is empty (might not capture the exact closing price)
        if len(data) == 0:
            st.warning("Unable to retrieve intraday data for the selected date. Defaulting to daily closing price.")
            # Download daily data as a fallback
            data = yf.download(stock_symbol, start=start_date, end=end_date)
    else:
        st.error("Intraday data can only be downloaded for a single date. Please select the same start and end date.")
        data = pd.DataFrame()  # Set empty dataframe to avoid errors
else:
    # Download daily data if checkbox is not selected or for different start/end dates
    if start_date == end_date:  # Check if start and end dates are the same
        # Download data for 3:15 PM of the selected date
        start_time = datetime.datetime.combine(start_date, datetime.time(15, 15))  # 3:15 PM
        end_time = datetime.datetime.combine(start_date, datetime.time(15, 30))  # 3:30 PM
        data = yf.download(stock_symbol, start=start_time, end=end_time)
    else:
        # Download daily data for the selected date range
        data = yf.download(stock_symbol, start=start_date, end=end_date)

# Check for available data before displaying elements
if len(data) > 0:
    # Display data frame and download button if data exists
    st.dataframe(data, width=800)
    st.download_button(label="Download CSV", data=data.to_csv().encode('utf-8'), key="csv_download", file_name="data.csv")

    # Create a Plotly figure (only if data has more than one day)
    if len(data) > 1:
        fig = px.line(data, x=data.index, y='Close', title=f'{stock_symbol} Stock Price', labels={'Close': 'Stock Price (INR)'})
        st.plotly_chart(fig)
else:
    # Display error message if no data found
    st.error("No data available for the selected time period. Please try adjusting the start and end dates.")

