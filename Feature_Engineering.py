import yfinance as yf
import pandas as pd 
import numpy as np
from sklearn.preprocessing import StandardScaler
import ruptures as rpt
import matplotlib.pyplot as plt
from pathlib import Path

# Get Bitcoin
ticker = ["BTC-USD"]

# Fetch historical prices
raw_data = yf.download(ticker, start="2021-09-17", end="2026-09-17")
df_bitcoin = raw_data.dropna().copy()

# Create log return
df_bitcoin["Log return"] = np.log(df_bitcoin["Close"]) - np.log(df_bitcoin["Close"].shift(1))

# Fetch 1-Year Treasury Constant Maturity Rate (DGS1)
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "Data" / "DGS1-2.csv"
df_dgs = pd.read_csv(DATA_PATH)

print("----------- 1-YEAR TREASURY CONSTANT MATURITY RATE ----------- \n", df_dgs.head())

print("\n ----------- BITCOIN ----------- \n", df_bitcoin.head())

df_bitcoin.columns = df_bitcoin.columns.get_level_values(0)

### Creating technical indicators
# Volatility proxy with rolling window = 5
df_bitcoin["Volatility_5_days"] = (df_bitcoin["Log return"].pow(2).rolling(5).mean())

# Volatility proxy with rolling window = 20
df_bitcoin["Volatility_20_days"] = (df_bitcoin["Log return"].pow(2).rolling(20).mean())

# Volatility proxy with rolling window = 100
df_bitcoin["Volatility_100_days"] = (df_bitcoin["Log return"].pow(2).rolling(100).mean())

# Log return from 1 day prior
df_bitcoin["Lag_1"] = df_bitcoin["Log return"].shift(1)

# Log return from 2 days prior
df_bitcoin["Lag_2"] = df_bitcoin["Log return"].shift(2)

# Log return from 3 days prior
df_bitcoin["Lag_3"] = df_bitcoin["Log return"].shift(3)

# Log return from 5 days prior ~ 1 business week ago
df_bitcoin["Lag_5"] = df_bitcoin["Log return"].shift(5)

# Log return from 20 days prior ~ 1 business month ago
df_bitcoin["Lag_20"] = df_bitcoin["Log return"].shift(20)

# Rolling features with a 3-period lookback window
df_bitcoin['Rolling_Mean_3d'] = df_bitcoin["Close"].rolling(window=3).mean()
df_bitcoin['Rolling_Std_3d'] = df_bitcoin["Close"].rolling(window=3).std()
df_bitcoin['Rolling_Max_3d'] = df_bitcoin["Close"].rolling(window=3).max()

# Rolling features with a 5-period lookback window
df_bitcoin['Rolling_Mean_5d'] = df_bitcoin["Close"].rolling(window=5).mean()
df_bitcoin['Rolling_Std_5d'] = df_bitcoin["Close"].rolling(window=5).std()
df_bitcoin['Rolling_Max_5d'] = df_bitcoin["Close"].rolling(window=5).max()

# Rolling features with a 20-period lookback window
df_bitcoin['Rolling_Mean_20d'] = df_bitcoin["Close"].rolling(window=20).mean()
df_bitcoin['Rolling_Std_20d'] = df_bitcoin["Close"].rolling(window=20).std()
df_bitcoin['Rolling_Max_20d'] = df_bitcoin["Close"].rolling(window=20).max()

# Exponential Moving Average (EMA) Crossovers
df_bitcoin["EMA_9"] = df_bitcoin["Close"].ewm(span=9, adjust=False).mean()
df_bitcoin["EMA_21"] = df_bitcoin["Close"].ewm(span=21, adjust=False).mean()
df_bitcoin["EMA_Cross_Diff"] = df_bitcoin["EMA_9"] - df_bitcoin["EMA_21"]

# Moving Average Convergence Divergence (12, 26, 9)
ema_12 = df_bitcoin["Close"].ewm(span=12, adjust=False).mean()
ema_26 = df_bitcoin["Close"].ewm(span=26, adjust=False).mean()
df_bitcoin["MACD_Line"] = ema_12 - ema_26
df_bitcoin["MACD_Signal"] = df_bitcoin["MACD_Line"].ewm(span=9, adjust=False).mean()
df_bitcoin["MACD_Diff"] = df_bitcoin["MACD_Line"] - df_bitcoin["MACD_Signal"]

# Relative Strength Index (RSI - 14)
delta = df_bitcoin["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
rs = avg_gain / avg_loss.replace(0, np.nan)
df_bitcoin["RSI_14"] = 100 - (100 / (1 + rs))

# Stochastic Oscillator (%K, %D - 14, 3)
low_14 = df_bitcoin["Low"].rolling(14).min()
high_14 = df_bitcoin["High"].rolling(14).max()
df_bitcoin["Stoch_%K"] = 100 * (df_bitcoin["Close"] - low_14) / (high_14 - low_14)
df_bitcoin["Stoch_%D"] = df_bitcoin["Stoch_%K"].rolling(3).mean()

# Rate of Change (ROC - 12)
df_bitcoin["ROC_12"] = df_bitcoin["Close"].pct_change(periods=12)

# Ensure date fields are in datetime format
df_dgs['observation_date'] = pd.to_datetime(df_dgs['observation_date'])
df_bitcoin.index = pd.to_datetime(df_bitcoin.index)

# Merge two datasets
df = pd.merge(
    df_dgs, 
    df_bitcoin, 
    left_on='observation_date', 
    right_index=True, 
    how='outer'
)

# Drop rows where 'Volatility_100_days' is missing
df = df.dropna(subset=['Volatility_100_days'])

# DSG 1 day prior
df["DGS1"] = df["DGS1"].shift(1)

print("\n ----------- FINAL MARGED DATASET BASED ON DATE --------- \n", df.head())
print("\n ----------- SUMMARY ----------- \n", df.info())
print("\n ----------- NUMBER OF MISSING VALUES ----------- \n", df.isna().sum())

print("Total columns:", len(df.columns))
print("Column List:")
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")
print("\n ----------- NUMBER OF MISSING VALUES ----------- \n", df.isna().sum())

# 1. Unique: No duplicate timestamps
is_unique = df['observation_date'].is_unique

# 2. Sorted: Dates are in strictly ascending order
is_sorted = df['observation_date'].is_monotonic_increasing

print(f"Unique:      {is_unique}")
print(f"Sorted:      {is_sorted}")
print(len(df))
df.to_csv("bitcoin_engineered_features.csv", index=False)

