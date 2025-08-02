import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("📈 Stock Performance Dashboard")

# Upload files
uploaded_file = st.sidebar.file_uploader(r"C:\Users\prati\OneDrive\Desktop\guvi\project2\merged_output.csv", type=["csv"])
sector_file = st.sidebar.file_uploader(r"C:\Users\prati\OneDrive\Desktop\guvi\project2\sector_mapping_updated.csv", type=["csv"])

# Load data
if uploaded_file and sector_file:
    df = pd.read_csv(uploaded_file)
    sector_map = pd.read_csv(sector_file)
else:
    st.warning("📂 Please upload both CSV files.")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip().str.title()
sector_map.columns = sector_map.columns.str.strip().str.title()

# Merge sector info
if 'Symbol' in df.columns and 'Symbol' in sector_map.columns:
    df = df.merge(sector_map, on='Symbol', how='left')
else:
    st.error("❌ 'Symbol' column missing in one of the datasets!")
    st.stop()

# Convert 'Date' column to datetime with correct format
df['Date'] = pd.to_datetime(df['Date'], format="%d-%m-%Y %H:%M")

# Sort by Symbol and Date
df.sort_values(['Symbol', 'Date'], inplace=True)

# Calculate Daily Return
df['Daily Return'] = df.groupby('Symbol')['Close'].pct_change()

# Annualized Average Return
df['Average Return'] = df.groupby('Symbol')['Daily Return'].transform('mean') * 252

# Volatility
volatility = df.groupby('Symbol')['Daily Return'].std() * np.sqrt(252)
volatility_df = volatility.sort_values(ascending=False).reset_index()
volatility_df.columns = ['Symbol', 'Volatility']

# Cumulative Return per stock
df['Cumulative Return'] = (1 + df['Daily Return']).groupby(df['Symbol']).cumprod()
latest_returns = df.groupby('Symbol')['Cumulative Return'].last().sort_values(ascending=False)
top_5 = latest_returns.head(5).index.tolist()

# Sector selection
available_sectors = df['Sector'].dropna().unique().tolist()
st.sidebar.markdown("## Filter Options")
selected_sectors = st.sidebar.multiselect("Select Sector(s)", options=available_sectors, default=available_sectors)
filter_button = st.sidebar.button("Apply Filter")

if filter_button:
    df = df[df['Sector'].isin(selected_sectors)]

# Section: Average Yearly Return by Sector
st.subheader("📊 Average Yearly Return by Sector")
if 'Sector' in df.columns and 'Average Return' in df.columns:
    avg_return_by_sector = df.groupby('Sector')['Average Return'].mean().sort_values(ascending=False)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=avg_return_by_sector.values, y=avg_return_by_sector.index, palette="viridis", ax=ax1)
    ax1.set_xlabel("Average Yearly Return (%)")
    ax1.set_ylabel("Sector")
    ax1.set_title("Average Yearly Return by Sector")
    st.pyplot(fig1)
else:
    st.warning("⚠️ 'Sector' or 'Average Return' column not found.")

# Section: Stock Price Correlation Heatmap
st.subheader("📉 Stock Price Correlation Heatmap")
correlation_df = df.pivot_table(index='Date', columns='Symbol', values='Close')
correlation_matrix = correlation_df.corr()

if correlation_matrix.shape[0] > 1:
    fig2, ax2 = plt.subplots(figsize=(12, 10))
    sns.heatmap(correlation_matrix, cmap='coolwarm', center=0, annot=False, linewidths=0.5)
    ax2.set_title("Stock Price Correlation Heatmap")
    st.pyplot(fig2)
else:
    st.warning("⚠️ Not enough stocks selected to compute correlation heatmap. Please select more than one sector or stock.")

# Section: Top 10 Most Volatile Stocks
st.subheader("⚡ Top 10 Most Volatile Stocks")
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.barplot(data=volatility_df.head(10), x='Volatility', y='Symbol', palette='rocket', ax=ax3)
ax3.set_title("Top 10 Most Volatile Stocks")
ax3.set_xlabel("Annualized Volatility")
ax3.set_ylabel("Stock Symbol")
st.pyplot(fig3)

# Section: Cumulative Return for Top 5 Performing Stocks
st.subheader("🚀 Cumulative Return for Top 5 Performing Stocks")
fig4, ax4 = plt.subplots(figsize=(10, 6))
for symbol in top_5:
    symbol_data = df[df['Symbol'] == symbol]
    ax4.plot(symbol_data['Date'], symbol_data['Cumulative Return'], label=symbol)
ax4.set_title("Top 5 Performing Stocks - Cumulative Return")
ax4.set_xlabel("Date")
ax4.set_ylabel("Cumulative Return")
ax4.legend()
st.pyplot(fig4)

# Section: Top 5 Gainers and Losers by Month
st.subheader("📅 Top 5 Gainers and Losers by Month")
df['Month'] = df['Date'].dt.month
monthly_return = df.groupby(['Month', 'Symbol'])['Daily Return'].sum().reset_index()

for month in range(1, 13):
    st.markdown(f"### 📆 Month: {month}")
    month_data = monthly_return[monthly_return['Month'] == month]
    top_gainers = month_data.sort_values(by='Daily Return', ascending=False).head(5)
    top_losers = month_data.sort_values(by='Daily Return').head(5)

    col1, col2 = st.columns(2)

    with col1:
        fig_gainers, ax_gainers = plt.subplots()
        sns.barplot(data=top_gainers, x='Daily Return', y='Symbol', palette='Greens', ax=ax_gainers)
        ax_gainers.set_title(f"Top 5 Gainers - Month {month}")
        st.pyplot(fig_gainers)

    with col2:
        fig_losers, ax_losers = plt.subplots()
        sns.barplot(data=top_losers, x='Daily Return', y='Symbol', palette='Reds_r', ax=ax_losers)
        ax_losers.set_title(f"Top 5 Losers - Month {month}")
        st.pyplot(fig_losers)
