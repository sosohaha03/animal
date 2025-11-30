from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/animals')
def animals():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data', 'sample_data_for_knime.json')

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)

