import yfinance as yf
import pandas as pd 
import numpy as np

# Get Bitcoin
ticker = ["BTC-USD"]

# Fetch historical prices
raw_data = yf.download(ticker, start="2022-1-1", end="2026-08-27")
df_bitcoin = raw_data.dropna().copy()

#print(df_bitcoin.head())

# Fetch 1-Year Treasury Constant Maturity Rate (DGS1)
df_dgs = pd.read_csv('/Users/quynhanhnguyen/Library/CloudStorage/GoogleDrive-quynhanh@aso.com.vn/My Drive/Nguyen_Thesis_2026-2027/Code source/Data/DGS1-2.csv')

#print(df_dgs.head())

# Create log return
df_bitcoin["Log return"] = df_bitcoin["Close"] - df_bitcoin["Close"].shift(1)

print(df_bitcoin.head())