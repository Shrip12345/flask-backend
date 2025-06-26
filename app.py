from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------------------
# Pydantic Models
# ---------------------------
class FinancialGoal(BaseModel):
    goal_name: str
    target_amount: float
    target_date: datetime
    importance_level: int

class IncomeExpense(BaseModel):
    monthly_income: float
    fixed_expenses: float
    current_savings: float

class PlanRequest(BaseModel):
    goals: List[FinancialGoal]
    finances: IncomeExpense

# ---------------------------
# Core Logic
# ---------------------------

# ---------------------------
# API Endpoints
# ---------------------------
@app.route('/add', methods=['GET'])
def add_number():
    number = request.args.get('number', type=int)
    if number is None:
        return jsonify({"error": "Please pass a number parameter"}), 400
    return jsonify({"result": number + 100})


@app.route('/addnum', methods=['POST'])
def add_numberrr():
    data = request.get_json()

    # Extracting values from the request body
    goal_name = data.get('goal_name')
    target_amount = data.get('target_amount')
    #target_date = data.get('target_date')
    #importance_level = data.get('importance_level')
    monthly_income = data.get('monthly_income')
    fixed_expenses = data.get('fixed_expenses')
    current_savings = data.get('current_savings')

    # OPTIONAL: Validation (e.g., ensure values are present and correct type)
    if not all([goal_name, target_amount, monthly_income, fixed_expenses, current_savings]):
        return jsonify({"error": "Missing one or more required fields"}), 400

    
    today = datetime.today()
    
    # Assuming target year/month are extracted from goal.target_date
    target_year = 2030
    target_month = 12
    
    # 1️⃣ Fix the incorrect syntax for months_left calculation
    months_left = (target_year - today.year) * 12 + (target_month - today.month)
    months_left = max(months_left, 1)

    # 2️⃣ Basic financial variables
    amount_needed = target_amount - current_savings
    available_to_save = monthly_income - fixed_expenses
    
    # 3️⃣ Add support for expected return (ROI)
    roi_percent = 0  # Change this to a dynamic field if you want to support user input
    monthly_rate = roi_percent / 12 / 100  # Convert annual % to monthly decimal

    # 4️⃣ Calculate required monthly savings based on compound interest formula
    if monthly_rate == 0:
        monthly_required = amount_needed / months_left
    else:
        monthly_required = amount_needed * monthly_rate / (((1 + monthly_rate) ** months_left) - 1)

    # 5️⃣ Advice and feasibility
    if monthly_required <= available_to_save:
        feasible = True
        advice = f"Invest ₹{monthly_required:.2f}/month at {roi_percent}% annual return to reach your goal."
        time_to_goal = None #f"{target_date.strftime('%B %Y')}"
    else:
        feasible = False
        shortfall = monthly_required - available_to_save
        advice = (
            f"You need to save ₹{shortfall:.2f} more monthly. "
            f"Try reducing expenses or increasing income."
        )
        time_to_goal = None

    # 6️⃣ Return structured output
    return jsonify({
        "goal_name": goal_name,
        "monthly_saving_required": round(monthly_required, 2),
        "feasible": feasible,
        "advice": advice,
        "completion_time_estimate": time_to_goal
    })

@app.route('/loadstocks', methods=['GET'])
def load_stocks():
    TOP_TICKERS = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS",
        "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "HINDUNILVR.NS", "ITC.NS"
    ]
    best = {"ticker": None, "marketCap": 0, "longName": None}
    for ticker in TOP_TICKERS:
        stock = yf.Ticker(ticker)
        info = stock.info
        mcap = info.get("marketCap")
        if mcap and mcap > best["marketCap"]:
            best.update({
                "ticker": ticker,
                "marketCap": mcap,
                "longName": info.get("longName")
            })
    if not best["ticker"]:
        return jsonify({"error": "No data available"}), 500
    usd_inr = 83
    mcap_inr = round(best["marketCap"] / 1e7 * usd_inr, 2)
    return jsonify({
        "company_name": best["longName"],
        "ticker": best["ticker"],
        "market_cap_usd": best["marketCap"],
        "market_cap_inr_crore": mcap_inr,
        "as_of": "Live"
    })

# ---------------------------
# Run Server
# ---------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
