from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = Flask(__name__)
CORS(app)

def method_SIPCalculate(amount_required, months_left, annual_roi):
    monthly_rate = annual_roi / 12 / 100  # Convert annual % to monthly decimal
    if monthly_rate == 0:
        monthly_required= amount_required / months_left
    else:
        monthly_required = amount_required * monthly_rate / (((1 + monthly_rate) ** months_left) - 1)
    return monthly_required

def method_return_parameters(goal_name,target_amount,monthly_income,
                         fixed_expenses,current_savings,months_left,
                         annual_roi):
    months_left = max(months_left, 1)
    amount_needed = target_amount - current_savings
    monthly_required=method_SIPCalculate(amount_needed, months_left, annual_roi)
    print("month required",monthly_required)
    available_to_save = monthly_income - fixed_expenses

    if monthly_required <= available_to_save:
        feasible = True
        advice = f"Great ! You can achieve the your goal"
    else:
        feasible = False
        advice = f"Sorry! You need to raise the investment amount or Rate of Interest to achieve this target!"
    return feasible, advice, round(monthly_required, 2)
    

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
    months_left =12
    annual_roi=12

    # OPTIONAL: Validation (e.g., ensure values are present and correct type)
    if not all([goal_name, target_amount, monthly_income, fixed_expenses, current_savings]):
        return jsonify({"error": "Missing one or more required fields"}), 400


    f,a,m=method_return_parameters(goal_name,target_amount,monthly_income,
                         fixed_expenses,current_savings,months_left,
                         annual_roi)

    # 6️⃣ Return structured output
    return jsonify({
        "goal_name": goal_name,
        "monthly_saving_required":m,
        "feasible": f,
        "advice": a,
    })

# ---------------------------
# Run Server
# ---------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
