from plyer import notification
import yfinance as yf

alerts = {}

def set_alert(stock, target_price):
    alerts[stock] = target_price

def check_alerts():
    for stock, target_price in alerts.items():
        price = yf.Ticker(stock).history(period="1d")["Close"].iloc[-1]
        if price >= target_price:
            notification.notify(
                title="Stock Alert!",
                message=f"{stock} has reached {target_price}!",
                timeout=5
            )
            del alerts[stock]
