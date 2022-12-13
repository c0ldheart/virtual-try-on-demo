# custom handler file

# model_handler.py

"""
ModelHandler defines a custom model handler - FB's Detectron model.
"""
import os
from models.networks import ResUnetGenerator, load_checkpoint
from models.afwm import AFWM
from typing import List, Dict
import torch
from ts.torch_handler.base_handler import BaseHandler

class ModelHandler(BaseHandler):
    """
    A custom model handler implementation.
    """

    def __init__(self):
        self._context = None
        self.initialized = False

    def initialize(self, context):
        """
        Initialize model. This will be called during model loading time
        :param context: Initial context contains model server system properties.
        :return:
        """
        self._context = context
        self.manifest = context.manifest
        properties = context.system_properties
        
        warp_model_checkpoint_dir = properties.get("warp_model_checkpoint_dir")
        gen_model_checkpoint_dir = properties.get("gen_model_checkpoint_dir")
        
        # defining and loading model
        self.warp_model = AFWM(3)
        load_checkpoint(self.warp_model, warp_model_checkpoint_dir)

        self.gen_model = ResUnetGenerator(7, 4, 5, ngf=64)
        load_checkpoint(self.gen_model, gen_model_checkpoint_dir)

        self.initialized = True
        
    def preprocess(self, requests: List[Dict[str, bytearray]]):
        """
        Transform raw input into model input data.
        :param batch: list of raw requests, should match batch size
        :return: list of preprocessed model input data
        """
        # Take the input data and make it inference ready
        preprocessed_data = requests[0].get("data")
        if preprocessed_data is None:
            preprocessed_data = requests[0].get("body")

        return preprocessed_data

    def inference(self, model_input: torch.Tensor):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        # Do some inference call to engine here and return output

        source_image, target_cloth_image, target_cloth_mask = model_input
        with torch.no_grad():
            warped_cloth, _, _, warped_cloth_mask = self.warp_model(source_image.cuda(), target_cloth_image.cuda(), target_cloth_mask.cuda())

            gen_inputs = torch.cat([source_image.cuda(), warped_cloth, warped_cloth_mask], 1)
            gen_outputs = self.gen_model(gen_inputs)
            p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
            p_rendered = torch.tanh(p_rendered)
            m_composite = torch.sigmoid(m_composite)
            m_composite = m_composite * warped_cloth_mask
            p_tryon = warped_cloth * m_composite + p_rendered * (1 - m_composite)

        return p_tryon

    def postprocess(self, inference_output: List[torch.Tensor]):
        """
        Return inference result.
        :param inference_output: list of inference output
        :return: list of predict results
        """
        # Take output from network and post-process to desired format
        postprocess_output = inference_output
        return postprocess_output

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