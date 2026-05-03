
import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os

# ------------------------------
# CONFIG
# ------------------------------
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_SENDER")

# NIFTY 50 (Large Cap Universe)
STOCKS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS",
    "ITC.NS","HINDUNILVR.NS","LT.NS","SBIN.NS","BHARTIARTL.NS",
    "KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS",
    "MARUTI.NS","TITAN.NS","SUNPHARMA.NS","ULTRACEMCO.NS",
    "ONGC.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","WIPRO.NS",
    "HCLTECH.NS","ADANIENT.NS","ADANIPORTS.NS","TATASTEEL.NS",
    "TATAMOTORS.NS","BAJAJFINSV.NS","NESTLEIND.NS","BRITANNIA.NS",
    "INDUSINDBK.NS","TECHM.NS","CIPLA.NS","DIVISLAB.NS",
    "APOLLOHOSP.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS",
    "JSWSTEEL.NS","HEROMOTOCO.NS","HDFCLIFE.NS","SBILIFE.NS",
    "BPCL.NS","IOC.NS","UPL.NS","BAJAJ-AUTO.NS","ADANIGREEN.NS"
]

# ------------------------------
# FETCH DATA
# ------------------------------
def fetch_data():
    print("Fetching market data...")

    data_dict = {}

    for stock in STOCKS:
        try:
            df = yf.download(stock, period = "3mo", interval ="1d", auto_adjust = True)
            if df.empty:
                print (f"No Data: {stock}")
                continue
            data_dict[stock]=df

        except Exception as e:
            print(f"Error fetching {stock}:{e}")
    return data_dict

    # return yf.download(STOCKS, period="3mo", interval="1d", group_by="ticker", auto_adjust=True)

# ------------------------------
# SHORT TERM STRATEGY (Momentum)
# ------------------------------
def short_term(data_dict):
    scores = []

    for stock, data in data_dict.items():
        try:
            # data = df[stock].dropna()

            if len(data) < 20:
                continue

            data["SMA5"] = data["Close"].rolling(5).mean()
            data["SMA20"] = data["Close"].rolling(20).mean()
            data["AvgVol"] = data["Volume"].rolling(10).mean()

            latest = data.iloc[-1]

            if (latest["SMA5"] > latest["SMA20"]):
                score += 1
            
            if (latest["Volume"] > latest["AvgVol"]):
                score += 1
            change = (latest["Close"] - data["Close"].iloc[-5])/data["Close"].iloc[-5]
            if change>0:
                score += 1
            if score>0:
                score.append((stock,score))
        except:
            continue

    scores.sort(key=lambda x: x[1], reverse = True)
    return [s[0] for s in scores[:5]]

# ------------------------------
# LONG TERM STRATEGY (Trend)
# ------------------------------
def long_term(data_dict):
    scores = []

    for stock, data in data_dict.items():
        try:
            # data = df[stock].dropna()

            if len(data) < 100:
                continue

            data["SMA50"] = data["Close"].rolling(50).mean()
            data["SMA200"] = data["Close"].rolling(100).mean()

            latest = data.iloc[-1]

            score = 0

            if (latest["Close"] > latest["SMA50"]):
                score += 1

            if (latest["SMA50"] > latest["SMA200"]):
                score += 1
            
            change = (latest["Close"] - data["Close"].iloc[-20])/data["Close"].iloc[-20]
            if change > 0:
                score += 1
            
            if score > 0:
                score.append((stock,score))

        except:
            continue

    scores.sort(key=lambda x: x[1], reverse = True)

    return [s[0] for s in scores [:5]]

# ------------------------------
# SEND EMAIL (GMAIL)
# ------------------------------
def send_email(short_list, long_list):
    body = "📊 Daily Stock Scan (Large Cap - Nifty 50)\n\n"

    body += "🔴 Short-Term (Momentum Picks):\n"
    if short_list:
        for s in short_list:
            body += f"- {s}\n"
    else:
        body += "No strong signals\n"

    body += "\n🟢 Long-Term (Trend Picks):\n"
    if long_list:
        for s in long_list:
            body += f"- {s}\n"
    else:
        body += "No strong signals\n"

    msg = MIMEText(body)
    msg["Subject"] = "Daily Stock Scan"
    msg["From"] = "abhishekag.iitr09@gmail.com"
    msg["To"] = "abhishek.npti@gmail.com"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("abhishekag.iitr09@gmail.com", "ifev wxkl mibo vrcf")
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email failed:", e)

# ------------------------------
# MAIN
# ------------------------------
def main():
    print("Running stock scan...")

    df = fetch_data()

    short_list = short_term(df)
    long_list = long_term(df)

    print("Short-term:", short_list)
    print("Long-term:", long_list)

    send_email(short_list, long_list)

# RUN
main()
