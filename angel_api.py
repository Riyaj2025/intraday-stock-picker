from SmartApi import SmartConnect
import pandas as pd
import datetime
import pyotp

# 🔐 Angel One SmartAPI credentials
API_KEY = "bQe7PD3Y"
CLIENT_CODE = "AAAU739571"
MPIN = "7361"
TOTP_SECRET = "XMPEUCQH4MCYBOBOY7CMBXLMKM"

# Initialize SmartAPI
smartapi = SmartConnect(api_key=API_KEY)

def login():
    try:
        # Generate TOTP using secret
        otp = pyotp.TOTP(TOTP_SECRET).now()

        # ⚠️ Login using MPIN instead of password
        data = smartapi.generateSession(CLIENT_CODE, MPIN, otp)


        if data and data.get("status") and "data" in data:
            print("✅ Login successful.")
            return data["data"]["refreshToken"]
        else:
            print("❌ Login failed. Server response:")
            print(data)
            return None
    except Exception as e:
        print("❌ Exception during login:", e)
        return None

def get_intraday_candles(token, interval="FIVE_MINUTE", duration=1):
    try:
        now = datetime.datetime.now()
        from_date = now - datetime.timedelta(days=duration)
        to_date = now

        params = {
            "exchange": "NSE",
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date.strftime('%Y-%m-%d %H:%M'),
            "todate": to_date.strftime('%Y-%m-%d %H:%M')
        }

        data = smartapi.getCandleData(params)

        if "data" in data:
            df = pd.DataFrame(data["data"], columns=[
                "timestamp", "open", "high", "low", "close", "volume"
            ])
            return df
        else:
            print("⚠️ No candle data returned.")
            return pd.DataFrame()

    except Exception as e:
        print(f"❌ Error fetching candles for token {token}: {e}")
        return pd.DataFrame()
