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

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload():
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

    # print(request.files)
    # # 从请求中获得文件
    # file = request.files['file']

    # # 转化为字节
    # img_bytes = file.read()
    # image = Image.open(io.BytesIO(img_bytes))
    # # 保存图片
    # image.save(file.filename)

    # url = {"imageurl": file.filename}
    # url = json.dumps(url)
    # print('图片url（现在是文件名）', url)

    # return url

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

if __name__ == '__main__':
    predictor = Predictor()
    print("model initializing...")
    predictor.initialize()
    print("model initialized")

    app.run(debug=True , host='192.168.173.23', port=5000)