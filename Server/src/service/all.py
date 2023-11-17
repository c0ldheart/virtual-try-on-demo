import os, sys
import cv2
from PIL import Image
import numpy as np
import glob
import warnings
import argparse


def print_line(msg):
    print("\033[32m-------------------------------------------\033[0m")
    print("\033[32m%s\033[0m" % msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--person_image",
        "-p",
        type=str,
        default="/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On/input_images/man8.jpg",
        help="origin person image path",
    )
    parser.add_argument(
        "--openpose_dir",
        type=str,
        default="/home/belizabeth/zjk/openpose-master/build/examples/openpose",
        help="openpose project build dir",
    )
    parser.add_argument(
        "--densepose_dir",
        type=str,
        default="/home/belizabeth/zjk/TryYours-Virtual-Try-On",
        help="densepose project dir",
    )
    parser.add_argument(
        "--humanparsing_dir",
        type=str,
        default="/home/belizabeth/zjk/TryYours-Virtual-Try-On/Graphonomy-master",
        help="humanparsing_dir project dir",
    )
    parser.add_argument(
        "--clothes_dir",
        type=str,
        default="/home/belizabeth/zjk/VITONHD_dataset/test",
        help="clothes image dir",
    )
    parser.add_argument(
        "--preprocessed_dir",
        type=str,
        default="./preprocessed_dir",
        help="preprocessed dir, include resized image, openpose, densepose, seg, warped clothes",
    )
    parser.add_argument(
        "--warpmodel_dir",
        type=str,
        default="/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On/PF-AFN/PF-AFN_test",
        help="warpmodel",
    )
    # ------------------ Parse arguments and make dirs -----------------------------
    opt = parser.parse_args()
    cur_work_dir = os.getcwd()
    opt.preprocessed_dir = os.path.abspath(opt.preprocessed_dir)
    os.makedirs(name=opt.preprocessed_dir, exist_ok=True)
    cur_persson_file_name = os.path.basename(opt.person_image).split(".")[0]
    cur_persson_file_dir = os.path.join(opt.preprocessed_dir, cur_persson_file_name)
    preprocessed_dir_list = [
        "image",
        "openpose_img",
        "openpose_json",
        "densepose",
        "seg",
        "warped_clothes",
        "warped_mask",
    ]
    preprocessed_dir_dict = {}
    for i in range(0, len(preprocessed_dir_list)):
        path = os.path.join(cur_persson_file_dir, preprocessed_dir_list[i])
        os.makedirs(path, exist_ok=True)
        # print("makedir: %s" % path)
        preprocessed_dir_dict[preprocessed_dir_list[i]] = path

    # Read input image
    print("\033[32mLoad image from: \033[0m%s" % opt.person_image)
    img = cv2.imread(opt.person_image)

    # -------------------------- Resize input image -------------------------------------------
    img_resized = cv2.resize(img, (384, 512), interpolation=cv2.INTER_AREA)
    resized_person_image_path = os.path.join(
        preprocessed_dir_dict["image"], cur_persson_file_name + ".jpg"
    )
    cv2.imwrite(resized_person_image_path, img_resized, [cv2.IMWRITE_JPEG_QUALITY,100])
    print(
        "\033[32mResized person image saved at: \033[0m%s"
        % os.path.join(resized_person_image_path)
    )

    # ----------------------------Get openpose coordinate using posenet ---------------------------------
    print_line("Get openpose coordinate (rendered image and json file)")

    os.chdir(opt.openpose_dir)
    terminnal_command = (
        "./openpose.bin --model_pose BODY_25 --write_coco_json_variants 1 \
            --model_folder /home/belizabeth/zjk/openpose-master/models --display 0 --hand --disable_blending\
            --image_dir %s \
            --write_json %s \
            --write_images %s"
        % (
            preprocessed_dir_dict["image"],
            preprocessed_dir_dict["openpose_json"],
            preprocessed_dir_dict["openpose_img"],
        )
    )
    os.system(terminnal_command)
    print_line("")

    # Get parsing
    print("\033[32mGetting parsing at%s\033[0m" % opt.humanparsing_dir)
    os.chdir(opt.humanparsing_dir)
    terminnal_command = (
        "python exp/inference/inference.py \
        --loadmodel ./inference.pth \
        --img_path %s --output_path %s --output_name %s"
        % (
            resized_person_image_path,
            preprocessed_dir_dict["seg"],
            cur_persson_file_name,
        )
    )
    os.system(terminnal_command)

    # ------------------------------------------ Get densepose -----------------------------------
    print_line("Getting densepose at%s" % opt.densepose_dir)

    os.chdir(opt.densepose_dir)
    os.environ["MKL_THREADING_LAYER"] = "GNU"
    # os.system("export MKL_SERVICE_FORCE_INTEL=1")
    terminnal_command = (
        "python detectron2/projects/DensePose/apply_net.py \
        dump \
        detectron2/projects/DensePose/configs/densepose_rcnn_R_50_FPN_s1x.yaml \
        https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl \
        %s \
        --output output.pkl -v"
        % resized_person_image_path
    )
    # print(terminnal_command)

    os.system(terminnal_command)
    terminnal_command = "python get_densepose.py -p %s -s %s" % (
        resized_person_image_path,
        os.path.join(
            preprocessed_dir_dict["densepose"], os.path.basename(opt.person_image)
        ),
    )
    os.system(terminnal_command)

    # ---------------------------------------- Warp clothes ------------------------------------------------
    print_line("Warp clothes at%s" % opt.warpmodel_dir)
    os.chdir(opt.warpmodel_dir)
    terminnal_command = (
        "python -u eval_PBAFN_viton.py --name=%s \
    --resize_or_crop=none --batchSize=1 --gpu_ids=0 \
    --warp_checkpoint=/home/belizabeth/zjk/DCI-VTON-Virtual-Try-On/checkpoints/warp_viton.pth \
    --label_nc=13 --fineSize=512 --unpaired\
    --dataroot=%s \
    --preprocessed_dir=%s \
    --saved_path=%s"
        % (
            cur_persson_file_name,
            opt.clothes_dir,
            cur_persson_file_dir,
            preprocessed_dir_dict["warped_clothes"],
        )
    )
    os.system(terminnal_command)

    # ------------------------------------- try on -----------------------------------------------
    res_dir = os.path.join(cur_work_dir, "results", cur_persson_file_name)
    os.makedirs(res_dir, exist_ok=True)
    os.chdir(cur_work_dir)
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
        --unpaired"
        % (cur_persson_file_name, res_dir, opt.clothes_dir, cur_persson_file_dir)
    )
    os.system(terminnal_command)
    
