from flask import Flask, render_template, request, send_file
from angel_api import login, get_intraday_candles
from stock_logic import check_trade_score
import pandas as pd
import time
import datetime
import io

app = Flask(__name__)
top_50 = []
last_scan = None

@app.route("/", methods=["GET", "POST"])
def index():
    global top_50, last_scan
    top_50 = []
    if request.method == "POST":
        jwt = login()
        if not jwt:
            return render_template("index.html", error="Login failed.")

        df = pd.read_csv("nifty500.csv", sep=r"\s+", engine="python")
        df.columns = df.columns.str.strip().str.lower()

        picks = []
        for _, row in df.iterrows():
            try:
                symbol = row["symbol"]
                token = str(row["token"])
                result = check_trade_score(symbol, token)

                if result:
                    df_candle = get_intraday_candles(jwt, symboltoken=token)
                    if df_candle.empty:
                        continue
                    last_price = float(df_candle.iloc[-1]["close"])
                    last_volume = float(df_candle.iloc[-1]["volume"])
                    if last_price >= 100 and last_volume >= 100000:
                        picks.append(result)
            except:
                continue
            time.sleep(0.8)

        top_50 = sorted(picks, key=lambda x: x["score"], reverse=True)[:50]
        last_scan = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("index.html", picks=top_50, last_scan=last_scan)

@app.route("/download")
def download():
    fmt = request.args.get("format")
    if not top_50:
        return "No data to download. Please scan first.", 400

    df = pd.DataFrame(top_50)
    buf = io.BytesIO()

    if fmt == "csv":
        df.to_csv(buf, index=False)
        buf.seek(0)
        return send_file(buf, mimetype='text/csv', download_name="top_50_intraday.csv", as_attachment=True)
    elif fmt == "xlsx":
        df.to_excel(buf, index=False)
        buf.seek(0)
        return send_file(buf, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name="top_50_intraday.xlsx", as_attachment=True)
    else:
        return "Invalid format", 400

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
