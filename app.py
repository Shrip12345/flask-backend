from flask import Flask, request, jsonify

app = Flask(__name__)

str1 = "Hello, World!"

@app.route('/gett', methods=['POST'])
def gett():
    global str1
    data = request.get_json()
    name = data.get('name', 'World')
    str1 = "Hello, " + name  # ✅ update global variable
    return jsonify({"message": f"Name received: {str1}"})

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": str1})  # ✅ will now return updated str1

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
