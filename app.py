from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)

# List of top NSE tickers
TOP_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS",
    "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "HINDUNILVR.NS", "ITC.NS"
]

@app.route('/add', methods=['GET'])
def add_number():
    number = request.args.get('number', default=None, type=int)

    if number is None:
        return jsonify({"error": "Please pass a number parameter"}), 400

    result = number + 100
    return jsonify({"result": result})


@app.route('/loadstocks', methods=['GET'])
def load_stocks():
    best = {"ticker": None, "marketCap": 0, "longName": None}
    
    for ticker in TOP_TICKERS:
        stock = yf.Ticker(ticker)
        info = stock.info
        mcap = info.get("marketCap")  # in USD
        
        if mcap and mcap > best["marketCap"]:
            best.update({
                "ticker": ticker,
                "marketCap": mcap,
                "longName": info.get("longName")
            })
    
    if not best["ticker"]:
        return jsonify({"error": "No data available"}), 500

    # Convert market cap to INR (using dummy conversion rate)
    usd_inr = 83  # approximate
    mcap_inr = round(best["marketCap"] / 1e7 * usd_inr, 2)  # in crores

    return jsonify({
        "company_name": best["longName"],
        "ticker": best["ticker"],
        "market_cap_usd": best["marketCap"],
        "market_cap_inr_crore": mcap_inr,
        "as_of": "Live"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
