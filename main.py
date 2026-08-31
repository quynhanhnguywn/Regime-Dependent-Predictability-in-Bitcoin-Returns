import yfinance as yf
import pandas as pd 
import numpy as np

# Get Bitcoin
ticker = ["BTC-USD"]

# Fetch historical prices
raw_data = yf.download(ticker, start="2022-1-1", end="2026-08-27")
df_bitcoin = raw_data.dropna().copy()

# Create log return
df_bitcoin["Log return"] = df_bitcoin["Close"] - df_bitcoin["Close"].shift(1)

#print(df_bitcoin.head())

# Fetch 1-Year Treasury Constant Maturity Rate (DGS1)
df_dgs = pd.read_csv('/Users/quynhanhnguyen/Library/CloudStorage/GoogleDrive-quynhanh@aso.com.vn/My Drive/Nguyen_Thesis_2026-2027/Code source/Data/DGS1-2.csv')

print("----------- 1-YEAR TREASURY CONSTANT MATURITY RATE ----------- \n", df_dgs.head())

print("\n ----------- BITCOIN ----------- \n", df_bitcoin.head())

df_bitcoin.columns = df_bitcoin.columns.get_level_values(0)

# Ensure date fields are in datetime format
df_dgs['observation_date'] = pd.to_datetime(df_dgs['observation_date'])
df_bitcoin.index = pd.to_datetime(df_bitcoin.index)

# Merge two datasets
merged_df = pd.merge(
    df_dgs, 
    df_bitcoin, 
    left_on='observation_date', 
    right_index=True, 
    how='outer'
)

print("\n ----------- FINAL MARGED DATASET BASED ON DATE --------- \n", merged_df.head())
print("\n ----------- SUMMARY ----------- \n", merged_df.info())
print("\n ----------- NUMBER OF MISSING VALUES ----------- \n", merged_df.isna().sum())
