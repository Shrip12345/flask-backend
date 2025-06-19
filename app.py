from flask import Flask, request, jsonify

app = Flask(__name__)

str1 = " "

@app.route('/gett', methods=['GET'])
def gett():
    global str1
    name = request.args.get('message', 'World')  # ✅ get from query string
    str1 = "Hello, " + name
    return jsonify({"message": f"Name received: {str1}"})

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": str1})  # ✅ will now return updated str1

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
