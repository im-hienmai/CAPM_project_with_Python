# importing libraries

import streamlit as st 
import pandas as pd 
import yfinance as yf
import pandas_datareader.data as web
import datetime
import capm_functions
import numpy as np


st.set_page_config(page_title= "CAMP",
    page_icon = "chart_with_upwards_trend",
    layout = 'wide')

st.title("Capital Asset Pricing Model")

# getting input from user
col1, col2 = st.columns([1,1])
with col1:
    stock_list = st.multiselect("Choose 4 stocks", ('TSLA','AAPL','NFLX','MSFT','MGM','AMZN','NVDA','GOOGL'),['TSLA','AAPL','AMZN','GOOGL'])
with col2:
    year = st.number_input("Number of years",1,10)

# downloading data for SP500

end = datetime.date.today()
start = datetime.date(datetime.date.today().year-year, datetime.date.today().month, datetime.date.today().day)
SP500 = web.DataReader(['sp500'],'fred',start, end)
print(SP500.tail())

stocks_df = pd.DataFrame()

for stock in stock_list:
    data = yf.download(stock, period=f'{year}y')
    stocks_df[f'{stock}'] = data['Close']

stocks_df.reset_index(inplace = True)
SP500.reset_index(inplace = True)
SP500.columns = ['Date','sp500']
stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
stocks_df['Date'] = stocks_df['Date'].apply(lambda x:str(x)[:10])
stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
stocks_df = pd.merge(stocks_df,SP500, on = 'Date', how = 'inner')

col1, col2 = st.columns([1,1])
with col1:
    st.markdown('### Dataframe head')
    st.dataframe(stocks_df.head(),use_container_width = True)
with col2:
    st.markdown('### Dataframe tail')
    st.dataframe(stocks_df.tail(),use_container_width = True)


col1, col2 = st.columns([1,1])
with col1:
    st.markdown("### Price of all the Stocks")
    st.plotly_chart(capm_functions.interactive_plot(stocks_df))
with col2:
    st.markdown("### Price of all the Stocks(After Normalizing)")
    st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

stocks_daily_return = capm_functions.daily_return(stocks_df)
print(stocks_daily_return.head())

beta = {}
alpha = {}

for i in stocks_daily_return.columns:
    if i !='Date' and i !='SP500':
        a, b = capm_functions.calculate_beta(stocks_daily_return,i)

        beta[i] = b
        alpha[i] = a
print(beta, alpha)

beta_df = pd.DataFrame(columns=['Stock','Beta Value'])
beta_df['Stock'] = beta.keys()
beta_df['Beta Value'] = [str(round(i,2))for i in beta.values()]

with col1:
    st.markdown('### Calculated Beta Value')
    st.dataframe(beta_df, use_container_width = True)

rf = 0
rm = stocks_daily_return['sp500'].mean()*252

return_df = pd.DataFrame()

# Display calculated return values using CAPM
return_values = [rf + (beta[stock] * (rf - rm)) for stock in stock_list]
return_df = pd.DataFrame({'Stock': stock_list, 'Return Value': return_values})
return_df['Return Value'] = return_df['Return Value'].round(2)


with col2:
    st.markdown('### Calculated Return using CAPM')

    st.dataframe(return_df, use_container_width= True)