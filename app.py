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
def calculate_plan(goal: FinancialGoal, finances: IncomeExpense):
    today = datetime.today()
    months_left = (goal.target_date.year - today.year) * 12 + (goal.target_date.month - today.month)
    months_left = max(months_left, 1)
    amount_needed = goal.target_amount - finances.current_savings
    monthly_required = max(amount_needed / months_left, 0)
    available_to_save = finances.monthly_income - finances.fixed_expenses

    if monthly_required <= available_to_save:
        feasible = True
        advice = "Stay consistent and you'll reach your goal on time."
        time_to_goal = goal.target_date.strftime("%B %Y")
    else:
        feasible = False
        shortfall = monthly_required - available_to_save
        advice = f"You need to save ₹{shortfall:.2f} more monthly. Consider cutting non-essential expenses or increasing income."
        time_to_goal = None

    return {
        "goal_name": goal.goal_name,
        "monthly_saving_required": round(monthly_required, 2),
        "feasible": feasible,
        "advice": advice,
        "completion_time_estimate": time_to_goal
    }

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
    if not all([goal_name, target_amount, target_date, importance_level, monthly_income, fixed_expenses, current_savings]):
        return jsonify({"error": "Missing one or more required fields"}), 400

    # You had this check below but variable 'number' was never defined
    # So removed that part

    # Example echo back
    return jsonify({
        "goal_name": goal_name,
        "target_amount": target_amount+10,
        #"target_date": target_date,
        #"importance_level": importance_level,
        "monthly_income": monthly_income+20,
        "fixed_expenses": fixed_expenses+30,
        "current_savings": current_savings+40
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

@app.route('/loaddata', methods=['POST'])
def load_data():
    try:
        data = request.get_json()
        plan_request = PlanRequest(**data)
        response = [calculate_plan(goal, plan_request.finances) for goal in plan_request.goals]
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ---------------------------
# Run Server
# ---------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
