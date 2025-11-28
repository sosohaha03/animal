from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/animals')
def animals():
    with open('./data/animals_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
