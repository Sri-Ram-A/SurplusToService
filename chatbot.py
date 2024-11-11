from flask import Flask, request, jsonify
from flask_cors import CORS  # Importing CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/store_answer', methods=['POST'])
def store_answer():
    # Get JSON data from the request
    data = request.get_json(silent=True)
    print("Received data:", data)
    
    # Check if data is present
    if data is None:
        return jsonify({'status': 'error', 'message': 'No data received or JSON parsing failed'}), 400

    question = data.get('question')
    answer = data.get('answer')
    
    # Ensure both question and answer are provided
    if not question or not answer:
        return jsonify({'status': 'error', 'message': 'Both question and answer are required'}), 400

    # Load existing data if file exists, otherwise create an empty dictionary
    if os.path.exists("donations.json"):
        with open("donations.json", "r") as f:
            try:
                responses = json.load(f)
            except json.JSONDecodeError:
                responses = {}
    else:
        responses = {}

    # Update responses with new question-answer pair
    responses[question] = answer

    # Write updated data back to the JSON file
    with open("donations.json", "w") as f:
        json.dump(responses, f, indent=4)

    print("Updated JSON content:", responses)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)