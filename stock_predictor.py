import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import os

def stock_exists(stock_symbol):
    """Check if the stock exists by fetching basic info."""
    stock = yf.Ticker(stock_symbol)
    try:
        name = stock.info.get("longName", None)
        return bool(name)  # If there's a valid name, stock exists
    except:
        return False  # Stock does not exist

def predict_stock_price(stock_symbol):
    """Predicts stock price using Linear Regression on real stock data."""
    if not stock_exists(stock_symbol):
        return None, f"❌ Stock '{stock_symbol}' does not exist!"

    try:
        print(f"🔄 Fetching historical data for {stock_symbol}...")
        stock_data = yf.Ticker(stock_symbol).history(period="6mo")  # 6 months of data

        if stock_data.empty:
            return None, f"❌ No data found for {stock_symbol}"

        # Prepare dataset
        stock_data["Days"] = np.arange(len(stock_data))
        X = stock_data[["Days"]]
        y = stock_data["Close"]

        # Train-Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict next 10 days
        future_days = np.arange(len(stock_data), len(stock_data) + 10).reshape(-1, 1)
        predictions = model.predict(future_days)

        # Plot
        plt.figure(figsize=(10, 5))
        plt.plot(stock_data.index, stock_data["Close"], label="Actual Prices", color="blue")
        plt.plot(pd.date_range(stock_data.index[-1], periods=10, freq="D"), predictions, label="Predicted", linestyle="dashed", color="red")
        plt.xlabel("Date")
        plt.ylabel("Stock Price")
        plt.title(f"Stock Price Prediction for {stock_symbol}")
        plt.legend()

        # Save plot
        save_path = f"predictions/{stock_symbol}_prediction.png"
        os.makedirs("predictions", exist_ok=True)
        plt.savefig(save_path)
        plt.close()

        return save_path, None  # Return file path
    except Exception as e:
        return None, str(e)
