import os
import cv2
 
class Predictor():
    """
    A custom model handler implementation.
    """
    def __init__(self, cloth_id, human_image_path, name):
        self.name = name
        self.cloth_id = cloth_id
        self.human_image_path = human_image_path
        self.work_dir = "/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On"
        self.openpose_dir = "/home/belizabeth/zjk/openpose-1.6.0/build/examples/openpose"
        self.densepose_dir = "/home/belizabeth/zjk/TryYours-Virtual-Try-On"
        self.humanparsing_dir = "/home/belizabeth/zjk/TryYours-Virtual-Try-On/Graphonomy-master"
        self.clothes_dir = "/home/belizabeth/zjk/VITONHD_dataset/test"
        self.preprocessed_dir = "/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On/preprocessed_dir"
        self.warpmodel_dir = "/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On/PF-AFN/PF-AFN_test"
        self.preprocessed_dir_list = [
            "image",
            "openpose_img",
            "openpose_json",
            "densepose",
            "seg",
            "warped_clothes",
            "warped_mask",
        ]   
        self.preprocessed_dir_dict = {}
        
    def preprocess(self):
        print('start preprocess')
        try:
            self.init_preprocess()
            self.openpose()
            self.densepose()
            self.human_parse()
            self.warp_cloth(self.cloth_id)
        except Exception as e:
            print(e)
            return "preprocess fail"
        
    def init_preprocess(self) -> None:
        os.chdir(path=self.work_dir)
        self.preprocessed_dir = os.path.abspath(self.preprocessed_dir)
        os.makedirs(name=self.preprocessed_dir, exist_ok=True)
        img_src = cv2.imread(self.human_image_path)
        img_byte = img_src.tobytes()
        cur_persson_file_name = self.name
        cur_persson_file_dir = os.path.join(self.preprocessed_dir, cur_persson_file_name)

        self.preprocessed_dir_dict = {}
        for i in range(0, len(self.preprocessed_dir_list)):
            path = os.path.join(cur_persson_file_dir, self.preprocessed_dir_list[i])
            os.makedirs(path, exist_ok=True)
            self.preprocessed_dir_dict[self.preprocessed_dir_list[i]] = path
        print("\033[32mMake image at: \033[0m%s" % self.human_image_path)

    def openpose(self):
        print_line("Get openpose coordinate (rendered image and json file)")

        os.chdir(self.openpose_dir)
        terminnal_command = (
            "./openpose.bin --model_pose BODY_25 --write_coco_json_variants 1 \
                --model_folder /home/belizabeth/zjk/openpose-master/models --display 0 --hand --disable_blending\
                --image_dir %s \
                --write_json %s \
                --write_images %s"
            % (
                self.preprocessed_dir_dict["image"],
                self.preprocessed_dir_dict["openpose_json"],
                self.preprocessed_dir_dict["openpose_img"],
            )
        )
        os.system(terminnal_command)
        print_line("")
    
    def densepose(self):
        print_line("Getting densepose at%s" % self.densepose_dir)

        os.chdir(self.densepose_dir)
        os.environ["MKL_THREADING_LAYER"] = "GNU"
        # os.system("export MKL_SERVICE_FORCE_INTEL=1")
        terminnal_command = (
            "python detectron2/projects/DensePose/apply_net.py \
            dump \
            detectron2/projects/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml \
            https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl \
            %s \
            --output output.pkl -v"
            % self.human_image_path
        )
        # print(terminnal_command)

        os.system(terminnal_command)
        terminnal_command = "python get_densepose.py -p %s -s %s" % (
            self.human_image_path,
            os.path.join(
                self.preprocessed_dir_dict["densepose"], os.path.basename(self.name) + '.jpg'
            ),
        )
        os.system(terminnal_command)
        
    def human_parse(self):
        print("\033[32mGetting parsing at%s\033[0m" % self.humanparsing_dir)
        os.chdir(self.humanparsing_dir)
        terminnal_command = (
            "python exp/inference/inference.py \
            --loadmodel ./inference.pth \
            --img_path %s --output_path %s --output_name %s"
            % (
                self.human_image_path,
                self.preprocessed_dir_dict["seg"],
                self.name,
            )
        )
        os.system(terminnal_command)

    def warp_cloth(self, cloth_id):
        print_line("Warp clothes at%s" % self.warpmodel_dir)
        os.chdir(self.warpmodel_dir)
        terminnal_command = (
            "python -u eval_PBAFN_viton.py --name=%s \
        --resize_or_crop=none --batchSize=1 --gpu_ids=0 \
        --warp_checkpoint=/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On/checkpoints/warp_viton.pth \
        --label_nc=13 --fineSize=512 --unpaired\
        --dataroot=%s \
        --preprocessed_dir=%s \
        --saved_path=%s  \
        --cloth_id=%s"
            % (
                self.name,
                self.clothes_dir,
                os.path.join(self.preprocessed_dir,self.name),
                self.preprocessed_dir_dict["warped_clothes"],
                str(cloth_id)
            )
        )
        os.system(terminnal_command)
        
    def inference(self):
        """
        Internal inference methods
        :param model_input: transformed model input data
        :return: list of inference output in NDArray
        """
        res_dir = os.path.join(self.work_dir, "results", self.name)
        os.makedirs(res_dir, exist_ok=True)
        os.chdir(self.work_dir)
        terminnal_command = (
            "python test.py --plms --gpu_id 0 \
            --ddim_steps 100 \
            --person_name %s \
            --outdir %s \
            --config configs/viton512.yaml \
            --dataroot %s \
            --preprocessed_dir %s \
            --ckpt /home/belizabeth/zjk/DCI-VTON-Virtual-Try-On/checkpoints/viton512.ckpt \
            --n_samples 1 \
            --seed 23 \
            --scale 1 \
            --H 512 \
            --W 512 \
            --unpaired \
            --cloth_id=%s"
            % (self.name, res_dir, self.clothes_dir, os.path.join(self.preprocessed_dir, self.name), str(self.cloth_id))
        )
        try:
            os.system(terminnal_command)
        except Exception as e:
            print(e)
            return "inference fail", ""
        return None, os.path.join(res_dir, str(self.cloth_id)+'_'+self.name + ".png")
        
def print_line(msg):
    print("\033[32m-------------------------------------------\033[0m")
    print("\033[32m%s\033[0m" % msg)
