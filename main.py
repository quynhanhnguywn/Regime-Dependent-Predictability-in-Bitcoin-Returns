import yfinance as yf
import pandas as pd 
import numpy as np
from sklearn.preprocessing import StandardScaler

# Get Bitcoin
ticker = ["BTC-USD"]

# Fetch historical prices
raw_data = yf.download(ticker, start="2021-09-17", end="2026-09-17")
df_bitcoin = raw_data.dropna().copy()

# Create log return
df_bitcoin["Log return"] = np.log(df_bitcoin["Close"]) - np.log(df_bitcoin["Close"].shift(1))

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

# Drop null values
df = merged_df.dropna().copy()
### Creating technical indicators
# Volatility with rolling window = 5
df["Volatility_5_days"] = (df["Log return"].pow(2).rolling(5).mean()).pow(2)

# Volatility with rolling window = 20
df["Volatility_20_days"] = (df["Log return"].pow(2).rolling(20).mean()).pow(2)

# Volatility with rolling window = 100
df["Volatility_100_days"] = (df["Log return"].pow(2).rolling(100).mean()).pow(2)

# Today's return
df["Lag_1"] = df["Close"].shift(1)

# Yesterday's return
df["Lag_2"] = df["Close"].shift(2)

# The day before's return
df["Lag_3"] = df["Close"].shift(3)

# Return of 5 days ago ~ 1 business week ago
df["Lag_5"] = df["Close"].shift(5)

# Return of 20 days ago ~ 1 business month ago
df["Lag_20"] = df["Close"].shift(20)

# Rolling features with a 3-period lookback window
df['Rolling_Mean_3d'] = df["Close"].rolling(window=3).mean()
df['Rolling_Std_3d'] = df["Close"].rolling(window=3).std()
df['Rolling_Max_3d'] = df["Close"].rolling(window=3).max()

# Rolling features with a 5-period lookback window
df['Rolling_Mean_5d'] = df["Close"].rolling(window=5).mean()
df['Rolling_Std_5d'] = df["Close"].rolling(window=5).std()
df['Rolling_Max_5d'] = df["Close"].rolling(window=5).max()

# Rolling features with a 20-period lookback window
df['Rolling_Mean_20d'] = df["Close"].rolling(window=20).mean()
df['Rolling_Std_20d'] = df["Close"].rolling(window=20).std()
df['Rolling_Max_20d'] = df["Close"].rolling(window=20).max()

# Exponential Moving Average (EMA) Crossovers
df["EMA_9"] = df["Close"].ewm(span=9, adjust=False).mean()
df["EMA_21"] = df["Close"].ewm(span=21, adjust=False).mean()
df["EMA_Cross_Diff"] = df["EMA_9"] - df["EMA_21"]

# Moving Average Convergence Divergence (12, 26, 9)
ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
df["MACD_Line"] = ema_12 - ema_26
df["MACD_Signal"] = df["MACD_Line"].ewm(span=9, adjust=False).mean()
df["MACD_Diff"] = df["MACD_Line"] - df["MACD_Signal"]

# Relative Strength Index (RSI - 14)
delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
rs = avg_gain / avg_loss.replace(0, np.nan)
df["RSI_14"] = 100 - (100 / (1 + rs))

# Stochastic Oscillator (%K, %D - 14, 3)
low_14 = df["Low"].rolling(14).min()
high_14 = df["High"].rolling(14).max()
df["Stoch_%K"] = 100 * (df["Close"] - low_14) / (high_14 - low_14)
df["Stoch_%D"] = df["Stoch_%K"].rolling(3).mean()

# Rate of Change (ROC - 12)
df["ROC_12"] = df["Close"].pct_change(periods=12)

# Drop null values
df = df.dropna().copy()

print("Total columns:", len(df.columns))
print("Column List:")
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")
print("\n ----------- NUMBER OF MISSING VALUES ----------- \n", df.isna().sum())

df.to_csv("bitcoin_engineered_features.csv", index=False)

### Data splitting
# Define features (X) and target (y) from df
X = df.drop(columns=["observation_date","Log return"])
y = df["Log return"]

# Chronological split: 80% for training, 20% for testing
split_index = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# Standardize predictors
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

print(df.tail())