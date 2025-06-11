import sys
import os
import requests
import yfinance as yf
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, \
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer




import auth, stock_alerts, stock_predictor

# Suppress TensorFlow logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

API_KEY = "b8f649d415dc42e39f4a42efaca95180"

class StockApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Trading Bot")
        self.setGeometry(100, 100, 900, 700)
        self.stocks = ["AAPL", "TSLA", "GOOGL"]
        self.stock_alerts = {}

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton#add_stock {
                background-color: #43A047;
            }
            QPushButton#add_stock:hover {
                background-color: #388E3C;
            }
            QPushButton#alert_btn {
                background-color: #E53935;
            }
            QPushButton#alert_btn:hover {
                background-color: #C62828;
            }
            QTableWidget {
                background-color: #1E1E1E;
                border: 1px solid #333;
                gridline-color: #444;
                color: white;
                alternate-background-color: #2A2A2A;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
                padding: 5px;
                font-weight: bold;
                border: 1px solid #444;
            }
            QLabel {
                font-size: 14px;
                padding: 5px;
            }
            QComboBox {
                background-color: #1E1E1E;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        self.initUI()
        self.update_stock_table()
        self.auto_predict_stocks()
        self.fetch_news()

    def initUI(self):
        layout = QVBoxLayout()

        self.stock_selector = QComboBox(self)
        self.stock_selector.addItems(self.stocks)
        self.stock_selector.currentIndexChanged.connect(self.update_graph)
        layout.addWidget(self.stock_selector)

        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(2)
        self.stock_table.setHorizontalHeaderLabels(["Stock", "Price"])
        layout.addWidget(self.stock_table)

        self.update_btn = QPushButton("Update Stocks", self)
        self.update_btn.clicked.connect(self.update_stock_table)
        layout.addWidget(self.update_btn)

        self.prediction_img = QLabel(self)
        layout.addWidget(self.prediction_img)

        self.add_stock_btn = QPushButton("Add Stock", self)
        self.add_stock_btn.setObjectName("add_stock")
        self.add_stock_btn.clicked.connect(self.add_stock)
        layout.addWidget(self.add_stock_btn)

        self.set_alert_btn = QPushButton("Set Price Alert", self)
        self.set_alert_btn.setObjectName("alert_btn")
        self.set_alert_btn.clicked.connect(self.set_price_alert)
        layout.addWidget(self.set_alert_btn)

        self.export_csv_btn = QPushButton("Export to CSV", self)
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(self.export_csv_btn)

        self.news_label = QLabel(self)
        layout.addWidget(self.news_label)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stock_table)
        self.timer.timeout.connect(self.auto_predict_stocks)
        self.timer.timeout.connect(self.fetch_news)
        self.timer.start(10000)




    def update_stock_table(self):
        self.stock_table.setRowCount(len(self.stocks))
        for i, stock in enumerate(self.stocks):
            stock_data = self.fetch_stock_data([stock])
            if stock_data:
                price = stock_data[0][1]
                self.stock_table.setItem(i, 0, QTableWidgetItem(stock))
                self.stock_table.setItem(i, 1, QTableWidgetItem(str(price)))
                if stock in self.stock_alerts and price >= self.stock_alerts[stock]:
                    QMessageBox.information(self, "Price Alert", f"{stock} has reached ${price}!")
            else:
                self.stock_table.setItem(i, 0, QTableWidgetItem(stock))
                self.stock_table.setItem(i, 1, QTableWidgetItem("Invalid ❌"))

    def fetch_stock_data(self, stocks):
        data = []
        for stock in stocks:
            try:
                stock_info = yf.Ticker(stock).history(period="7d", interval="1d")
                if not stock_info.empty:
                    price = round(stock_info["Close"].iloc[-1], 2)
                    data.append((stock, price))
            except Exception as e:
                print(f"⚠️ Error fetching data for {stock}: {e}")
        return data

    def auto_predict_stocks(self):
        self.update_graph()

    def update_graph(self):
        selected_stock = self.stock_selector.currentText()
        img_path, error = stock_predictor.predict_stock_price(selected_stock)
        if error:
            QMessageBox.warning(self, "Prediction Failed", error)
        else:
            self.prediction_img.setPixmap(QPixmap(img_path))
            self.prediction_img.setScaledContents(True)

    def add_stock(self):
        stock, ok = QInputDialog.getText(self, "Add Stock", "Enter Stock Symbol:")
        if ok and stock:
            self.stocks.append(stock.upper())
            self.stock_selector.addItem(stock.upper())
            self.update_stock_table()

    
    def set_price_alert(self):
        stock, ok = QInputDialog.getItem(self, "Set Alert", "Select Stock:", self.stocks, 0, False)
        if ok:
            price, ok = QInputDialog.getDouble(self, "Set Alert", f"Set price alert for {stock}:")
            if ok:
                self.stock_alerts[stock] = price
                QMessageBox.information(self, "Alert Set", f"Alert set for {stock} at ${price}")

    def fetch_news(self):
        selected_stock = self.stock_selector.currentText()
        url = f"https://newsapi.org/v2/everything?q={selected_stock}&apiKey={API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
            if data["status"] == "ok" and data["articles"]:
                news_headline = data["articles"][0]["title"]
                self.news_label.setText(f"📰 News: {news_headline}")
            else:
                self.news_label.setText("No recent news found.")
        except Exception as e:
            self.news_label.setText("Error fetching news.")

    def export_to_csv(self):
        file_path, _ = QInputDialog.getText(self, "Export CSV", "Enter filename (without extension):")
        if file_path:
            data = [[self.stock_table.item(i, 0).text(), self.stock_table.item(i, 1).text()] for i in range(self.stock_table.rowCount())]
            pd.DataFrame(data, columns=["Stock", "Price"]).to_csv(f"{file_path}.csv", index=False)
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}.csv")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockApp()
    window.show()
    sys.exit(app.exec_())
