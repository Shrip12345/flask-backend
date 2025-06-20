from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add_number():
    number = request.args.get('number', default=None, type=int)

    if number is None:
        return jsonify({"error": "Please pass a number parameter"}), 400

    result = number + 100
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
