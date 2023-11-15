from typing import Dict
import hashlib
import os
import cv2
import numpy as np
class FileHelper():
    """
    处理文件的hash计算、保存等操作
    """
    def __init__(self, config:Dict):
        self.root = config['MODEL_PATH']
        self.storage_path = os.path.join(self.root, 'preprocessed_dir')
        self.hash2path = {}
        
    def save(self, file):
        file_hash = self.get_hash(file)
        if file_hash in self.hash2path:
            return 'file already exist!', self.hash2path[file_hash]
        else:
            file_path: str = self.get_path(self.storage_path, file_hash)
            npimg = np.frombuffer(file, np.uint8)
            img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            img_resized = cv2.resize(img, (384, 512), interpolation=cv2.INTER_AREA)
            cv2.imwrite(file_path, img_resized, [cv2.IMWRITE_JPEG_QUALITY,100])
            self.hash2path[file_hash] = file_path
            return 'new file saved!', file_hash, file_path
    
    def get_hash(self, file):

        # 使用 SHA-256 算法计算哈希值
        sha256_hash = hashlib.sha256(file)

        # 将哈希值转换为十六进制字符串表示
        hash_string = sha256_hash.hexdigest()

        return hash_string
    

        
    def get_path(self, target_dir, file_hash):
        dir_path = os.path.join(target_dir, file_hash, 'image')
        os.makedirs(dir_path, exist_ok=True)
        target_path = os.path.join(dir_path, file_hash+'.jpg')
        return target_path