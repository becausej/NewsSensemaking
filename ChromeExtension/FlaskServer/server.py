from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json  # Get data sent by the extension
    text = data.get('text', '')

    # TODO
    first_word = text.split()[0] if text else ''
    return jsonify({'first_word': first_word, 'message': 'Success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    with open("output.txt", "w") as file:
      file.write(f"his\n")