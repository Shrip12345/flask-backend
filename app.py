from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
CORS(app)





@app.route('/top50', methods=['GET'])
def get_top_50():
     # Use a relative or absolute path
    file_path = os.path.join(os.path.dirname(__file__), 'new', 'combined_output.xlsx')
    
    df = pd.read_excel(file_path)  # Must be uploaded in the same directory
    df = df.head(50)
     # Optional: Clean NaNs
    df.fillna("", inplace=True)

    # Convert to dictionary
    data={
            "Scheme_Name": df["Scheme_Name"].tolist(),
            "1Y_Return": df["1Y_Return"].tolist(),
            "3Y_Return": df["3Y_Return"].tolist(),
            "5Y_Return": df["5Y_Return"].tolist(),
            "Benchmark": df["Benchmark"].tolist()
        }
    
    return jsonify(data)


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

    data = request.get_json()

    # Extract and validate fields
    try:
        target_amount = float(data.get('target_amount', 0))
        months_left = int(data.get('months_left', 0))
        investtype = "hello"
        #data.get('investtype', '').strip()
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input format"}), 400

    if not all([target_amount, months_left, investtype]):
        return jsonify({"error": "Missing one or more required fields"}), 400

    # Simple monthly SIP calculation (without interest)
    monthly_saving_required = round(target_amount / months_left, 2)

    # Return structured output
    return jsonify({
        "monthly_saving_required": monthly_saving_required,
        "feasible": months_left > 0,
        "advice": investtype
    })
    

    '''
    if months_left is None:
        months_left = 12
    else:
        months_left = int(months_left)
    annual_roi = float(data.get('annual_roi', 12))  # Default to 12% if not passed

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
    '''


@app.route('/top50funds', methods=['GET'])
def get_top_50_funds():
    # Use dynamic path to current file location
    base_path = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_path, 'new', 'combined_output.xlsx')

    # Read Excel file
    try:
        df = pd.read_excel(excel_path).head(50)
        # Add Sr. No. column
        df.reset_index(drop=True, inplace=True)
        df['sr_no'] = df.index + 1

        # Reorder and rename columns
        df = df[['sr_no', 'Scheme_Name', '1Y_Return', '3Y_Return', '5Y_Return']]
        df.columns = ['sr_no', 'scheme_name', 'return_1y', 'return_3y', 'return_5y']


         # Return under a top-level key
        return jsonify({'funds': df.to_dict(orient='records')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ---------------------------
# Run Server
# ---------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
