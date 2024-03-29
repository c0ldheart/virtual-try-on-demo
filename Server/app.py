from flask_cors import *
from flask import Flask, request, jsonify, send_file
from src.service.Predictor import Predictor
from src.service.FileHelper import FileHelper
app = Flask(__name__)
app.config['MODEL_PATH'] = '/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On'
CORS(app, resources=r'/*')

file_helper = FileHelper(app.config)
res_cache = {}
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
    file = file.read()
    message, file_hash, path = file_helper.save(file)
    print("文件保存：", path)
    return jsonify({'message': message, 'image_url': path})
  
@app.route('/tryon', methods=['POST'])
def tryon():
    cloth_id = request.form['clothId']
    # human_hash = request.form['humanHash']
    human_image = request.files['humanImage']
    if human_image.filename == '':
        return jsonify({'message': 'No file uploaded errorcode:2'})
    message, file_hash, human_path = file_helper.save(file=human_image.read())
    print(message)
    if (file_hash, cloth_id) in res_cache:
        return send_file(res_cache[(file_hash, cloth_id)])
    predictor = Predictor(cloth_id, human_path, file_hash)
    err = predictor.preprocess()
    if err != None:
        return jsonify({'message': err})
    err, res_path = predictor.inference()
    if err != None:
        return jsonify({'message': err})
    res_cache[(file_hash, cloth_id)] = res_path
    return send_file(res_path)
    return jsonify({'message': 'success'})
    

if __name__ == '__main__':
    app.run(debug=True , host='0.0.0.0', port=6001)
    # app.run(debug=True , host='0.0.0.0', port=6000, ssl_context=("/home/ubuntu/VITON01/FlaskServer/.well-known/certificate.crt", "/home/ubuntu/VITON01/FlaskServer/.well-known/private.key"))