from flask_cors import *
from flask import Flask, request, jsonify, send_file
import os
import io
from PIL import Image
import json
from src.service.predict import Predictor
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './images'
CORS(app, supports_credentials=True)

predictor = Predictor()
print("model initializing...")
predictor.initialize()
print("model initialized")
    
    
@app.route('/')
def hello_world():
    return 'Hello, World!!!'

@app.route('/upload', methods=['POST'])
def upload():
    print('Hello, World2!!!')
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded errorcode:1'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file uploaded errorcode:2'})
    filename = file.filename
    image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(image_url):
        return jsonify({'message': 'File already exists errorcode:3',
                        'image_url': image_url})

    file.save(image_url)
    print("文件保存：", image_url)
    return jsonify({'image_url': image_url})

@app.route('/predict', methods=['POST'])
def predict():


    # 获得json
    data = json.loads(request.data)
    image1_url = data['image1'][0]['response']['image_url']
    print("image1 url:", image1_url)

    image2_url = data['image2'][0]['response']['image_url']
    print("image2 url:", image2_url)

    print("preprocess...")
    predictor.preprocess(image1_url, image2_url)
    print("preprocess done")
    print("inference...")
    tryon_tensor = predictor.inference()
    print("inference done")
    result_path = predictor.postprocess(tryon_tensor)

    return send_file(result_path)
    # return jsonify({'res_path': result_path})
@app.route('/predict_test', methods=['POST'])
def predict_test():


    # 获得json
    # data = json.loads(request.data)
    image1_url = 'results/000001_0.jpg'
    

    image2_url = 'results/000001_0.jpg'
    

    print("preprocess...")
    predictor.preprocess(image1_url, image2_url)
    print("preprocess done")
    print("inference...")
    tryon_tensor = predictor.inference()
    print("inference done")
    result_path = predictor.postprocess(tryon_tensor)

    return send_file(result_path)
if __name__ == '__main__':

    app.run(debug=True , host='0.0.0.0', port=6000)
    # app.run(debug=True , host='0.0.0.0', port=6000, ssl_context=("/home/ubuntu/VITON01/FlaskServer/.well-known/certificate.crt", "/home/ubuntu/VITON01/FlaskServer/.well-known/private.key"))