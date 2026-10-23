# Regime-Dependent-Predictability-in-Bitcoin-Returns

## Dataset sourses:

* **Downloaded data range**: 09/17/2021 - 09/17/2026
* **Actual date range in final dataset**: 12/26/2021 - 09/16/2026
* **1-Year Treasury Constant Maturity Rate (DGS1)**: [Market Yield on U.S. Treasury Securities at 1-Year Constant Maturity, Quoted on an Investment Basis (DGS1).](https://fred.stlouisfed.org/series/dgs1)
* **Bitcoin (BTC-USD)**: yfinance package version 1.7.0. Downloads daily records and omits Adj Close columns.

## Target variable

* **Log return**: Daily log return calculated as $r_t = \ln(P_t / P_{t-1})$, serving as a stationary measure of price change.

## Predictors

### Base Market Data & Macro Indicators

* **DGS1**: 1-Year Treasury Constant Maturity Rate; risk-free interest rate benchmark obtained from FRED. 
Since the rate becomes available by 6PM ET and Bitcoin update closing price at 7PM ET, DSG1 is shifted one day prior to prevent look-ahead bias.
* **Open**: Bitcoin's opening price at the start of the trading day (00:00 UTC).
* **High**: Peak price reached by Bitcoin during the 24-hour trading session.
* **Low**: Lowest price recorded for Bitcoin during the 24-hour trading session.
* **Close**: Bitcoin's final closing price at the end of the trading day (23:59 UTC).
* **Volume**: Total aggregate trading volume executed across exchanges during the day.

---

### Return Metrics & Lagged Features

* **Lag_1**: Log return from 1 day prior ($t-1$).
* **Lag_2**: Log return from 2 days prior ($t-2$).
* **Lag_3**: Log return from 3 days prior ($t-3$).
* **Lag_5**: Log return from 5 days prior ($t-5$).
* **Lag_20**: Log return from 20 days prior ($t-20$).

---

### Historical Volatility Proxies

* **Volatility_5_days**: volatility proxy with 5-day rolling window capturing short-term volatility shifts.
* **Volatility_20_days**: volatility proxy with 20-day rolling window capturing medium-term volatility shifts.
* **Volatility_100_days**: volatility proxy with 100-day rolling window capturing long-term volatility shifts.

---

### Rolling Window Statistics

* **Rolling_Mean_3d / 5d / 20d**: Moving average of close price calculated across 3-day, 5-day, and 20-day windows.
* **Rolling_Std_3d / 5d / 20d**: Standard deviation of close price across 3-day, 5-day, and 20-day windows to track localized price dispersion.
* **Rolling_Max_3d / 5d / 20d**: Highest single price (or maximum close price) observed over the past 3, 5, or 20 trading days.

---

### Trend & Momentum Technical Signals

* **EMA_9**: 9-day Exponential Moving Average, prioritizing recent price changes for short-term trends.
* **EMA_21**: 21-day Exponential Moving Average, tracking medium-term trend direction.
* **EMA_Cross_Diff**: Distance between short- and medium-term trends ($\text{EMA}_9 - \text{EMA}_{21}$); signals bullish crossovers when positive and bearish crossovers when negative.
* **MACD_Line**: Moving Average Convergence Divergence line ($EMA_{12} - EMA_{26}$); quantifies directional momentum.
* **MACD_Signal**: 9-day EMA of the MACD Line, serving as the buy/sell trigger line.
* **MACD_Diff**: MACD histogram value ($\text{MACD}_{\text{Line}} - \text{MACD}_{\text{Signal}}$); indicates acceleration or exhaustion of momentum.
* **RSI_14**: 14-day Relative Strength Index (0–100 scale); values above 70 indicate overbought conditions, while values below 30 indicate oversold conditions.
* **Stoch_%K**: Stochastic Oscillator fast line (%K); measures current close price relative to the 14-day high-low range.
* **Stoch_%D**: 3-day moving average of `Stoch_%K`, acting as a smoothed signal line.
* **ROC_12**: 12-day Rate of Change; measures percentage velocity of price movements over a 12-day period.

## Data Quality:

After feature engineering from raw Bitcoin data, Bitcoin and DSG1 are merged according to calendar date. The first 100 observation dates used for initializing engineered features are dropped. There are 35 columns and 1726 rows. Observation date is unique, sorted, and consecutive. There is only DSG1 column records 546 missing values due to weekends and holidays.