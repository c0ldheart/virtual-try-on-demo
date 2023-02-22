from ..models.networks import ResUnetGenerator, load_checkpoint
from ..models.afwm import AFWM
from typing import List, Dict
import torch
from .data import get_transform, cloth_masking_with_grabcut
from PIL import Image
import torchvision.transforms as transforms
import os
from torchvision import utils
import time
class Predictor():
    """
    A custom model handler implementation.
    """

    def __init__(self):
        self.warp_model = None
        self.gen_model = None
        self.source_person_image_path = ""
        self.target_cloth_image_path = ""

        self.source_person_image_tensor = None
        self.target_cloth_image_tensor = None

        self.target_cloth_mask_path = ""
        self.target_cloth_mask_tensor = None
    def initialize(self):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """


        warp_model_checkpoint_dir = "./checkpoint/ckp/non_aug/PFAFN_warp_epoch_101.pth"
        gen_model_checkpoint_dir = "./checkpoint/ckp/non_aug/PFAFN_gen_epoch_101.pth"
        
        # defining and loading model
        self.warp_model = AFWM(3).cuda()
        load_checkpoint(self.warp_model, warp_model_checkpoint_dir)
        print("warp_model loaded")

        self.gen_model = ResUnetGenerator(7, 4, 5, ngf=64).cuda()
        load_checkpoint(self.gen_model, gen_model_checkpoint_dir)
        print("gen_model loaded")


        self.initialized = True
    def preprocess(self, image1_path, image2_path):
        self.source_person_image_path = image1_path
        self.target_cloth_image_path = image2_path
        transfromA = get_transform(normalize=True)
        transfromB = get_transform(normalize=False)

        start = time.time()
        source_person_image = Image.open(image1_path).convert('RGB')
        self.source_person_image_tensor = transfromA(source_person_image).unsqueeze(0)
        print(f"Line 1 takes {time.time()-start:.6f} seconds")

        start = time.time()
        target_cloth_image = Image.open(image2_path).convert('RGB')
        self.target_cloth_image_tensor = transfromA(target_cloth_image).unsqueeze(0)
        print(f"Line 2 takes {time.time()-start:.6f} seconds")
            
        start = time.time()
        self.target_cloth_mask_path = cloth_masking_with_grabcut(image2_path, "./masks")
        print(f"Line 3 takes {time.time()-start:.6f} seconds")

        start = time.time()
        target_cloth_mask = Image.open(self.target_cloth_mask_path).convert('L')
        self.target_cloth_mask_tensor = transfromB(target_cloth_mask).unsqueeze(0)
        print(f"Line 4 takes {time.time()-start:.6f} seconds")

    def inference(self):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        # Do some inference call to engine here and return output
        if self.source_person_image_tensor is None or self.target_cloth_image_tensor is None:
            print("source_person_image_tensor or target_cloth_image_tensor is None")
            return None

        with torch.no_grad():
            warped_cloth, last_flow, _, warped_cloth_mask = self.warp_model(self.source_person_image_tensor.cuda(), self.target_cloth_image_tensor.cuda(), self.target_cloth_mask_tensor.cuda())

            gen_inputs = torch.cat([self.source_person_image_tensor.cuda(), warped_cloth, warped_cloth_mask], 1)
            gen_outputs = self.gen_model(gen_inputs)
            p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
            p_rendered = torch.tanh(p_rendered)
            m_composite = torch.sigmoid(m_composite)
            m_composite = m_composite * warped_cloth_mask
            p_tryon = warped_cloth * m_composite + p_rendered * (1 - m_composite)


        return p_tryon

    def postprocess(self, tryon_tensor):
        """
        Return inference result.
        :param inference_output: list of inference output
        :return: list of predict results
        """
        # tensor to image and save
        tryon_tensor = tryon_tensor.squeeze().cpu()


        # 将 tensor 转换为 PIL.Image
        # output_image = transforms.ToPILImage()(tryon_tensor)

        # 保存图片到本地
        save_path = os.path.join('./results', os.path.basename(self.source_person_image_path))
        utils.save_image(tryon_tensor, save_path, nrow=int(1), normalize=True, range=(-1, 1), )

        # output_image.save(save_path)
        print("tryon saved at: ", save_path)
        return save_path

    def handle(self, data, context):
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        if not self.initialized:
          self.initialized(context)
          
        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)