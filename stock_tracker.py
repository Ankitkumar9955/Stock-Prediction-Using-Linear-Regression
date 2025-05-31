import yfinance as yf
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

def fetch_stock_data(stocks):
    """Fetches stock prices for given stocks."""
    data = []
    for stock in stocks:
        try:
            stock_info = yf.Ticker(stock).history(period="1d")
            if not stock_info.empty:
                price = round(stock_info["Close"].iloc[-1], 2)
                data.append((stock, price))
            else:
                print(f"⚠️ No data available for {stock}")
        except Exception as e:
            print(f"❌ Error fetching {stock}: {e}")
    return data

def update_stock_table(table, stocks):
    """Updates stock price table in UI."""
    print(f"🔄 Fetching stock data for: {stocks}")  # Debugging print
    data = fetch_stock_data(stocks)
    print(f"✅ Stock Data Fetched: {data}")  # Debugging print

    table.setRowCount(len(data))
    for i, (stock, price) in enumerate(data):
        table.setItem(i, 0, QTableWidgetItem(stock))
        table.setItem(i, 1, QTableWidgetItem(str(price)))
