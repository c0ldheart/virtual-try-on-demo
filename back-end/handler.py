# custom handler file

# model_handler.py

"""
ModelHandler defines a custom model handler - FB's Detectron model.
"""
import os

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
        
        model_dir = properties.get('model_dir')
        
        model_file_path = os.path.join(model_dir, 'trained_model.pth')
        model_config_path = os.path.join(model_dir, 'trained_model_config.yaml')
        
        # defining and loading detectron model
        self.model = lp.Detectron2LayoutModel(model_config_path, model_file_path,
                                              extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                                              label_map = {
                                                1: "TextRegion",
                                                2: "ImageRegion",
                                                3: "TableRegion",
                                                4: "MathsRegion",
                                                5: "SeparatorRegion",
                                                6: "OtherRegion"
                                              })
        
        self.initialized = True
        
    def preprocess(self, data):
        """
        Transform raw input into model input data.
        :param batch: list of raw requests, should match batch size
        :return: list of preprocessed model input data
        """
        # Take the input data and make it inference ready
        preprocessed_data = data[0].get("data")
        if preprocessed_data is None:
            preprocessed_data = data[0].get("body")

        return preprocessed_data

    def inference(self, model_input):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        # Do some inference call to engine here and return output
        model_output = self.model.detect(model_input)
        return model_output

    def postprocess(self, inference_output):
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