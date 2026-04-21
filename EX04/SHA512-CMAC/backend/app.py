from flask import Flask, request, jsonify
from flask_cors import CORS
from sha512_visualizer import SHA512Visualizer
from cmac_visualizer import CMACVisualizer

app = Flask(__name__)
CORS(app)

@app.route('/api/sha512', methods=['POST'])
def compute_sha512():
    data = request.json
    message = data.get('message', '')
    
    visualizer = SHA512Visualizer()
    result = visualizer.compute_with_steps(message)
    
    return jsonify(result)

@app.route('/api/cmac', methods=['POST'])
def compute_cmac():
    data = request.json
    message = data.get('message', '')
    key = data.get('key', '')
    
    visualizer = CMACVisualizer()
    result = visualizer.compute_with_steps(message, key)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)