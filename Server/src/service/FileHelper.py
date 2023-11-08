from typing import Dict
import hashlib
import os
class FileHelper():
    """
    处理文件的hash计算、保存等操作
    """
    def __init__(self, config:Dict):
        self.root = config['MODEL_PATH']
        self.storage_path = os.path.join(self.root, 'storage')
        self.hash2path = {}
        
    def save(self, file):
        file_hash = self.get_hash(file)
        if file_hash in self.hash2path:
            return 'file already exist!', self.hash2path[file_hash]
        else:
            file_path = self.get_path(file_hash)
            file.save(file_path)
            self.hash2path[file_hash] = file_path
            return 'new file saved!', file_path
    
    def get_hash(self, file):

        # 使用 SHA-256 算法计算哈希值
        sha256_hash = hashlib.sha256(file.read())

        # 将哈希值转换为十六进制字符串表示
        hash_string = sha256_hash.hexdigest()

        return hash_string
    

        
    def get_path(self, file_hash):
        dir_path = os.path.join(self.storage_path, file_hash, 'image')
        os.makedirs(dir_path, exist_ok=True)
        target_path = os.path.join(dir_path, 'source.jpg')
        return target_path