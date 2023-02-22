import torch.utils.data as data
from PIL import Image
import torchvision.transforms as transforms
import os
import cv2
import numpy as np


def get_transform(normalize):

    transform_list = []
    transform_list.append(transforms.Scale([256,192]))   
    transform_list += [transforms.ToTensor()]
    if normalize:
        transform_list += [transforms.Normalize((0.5, 0.5, 0.5),
                                                (0.5, 0.5, 0.5))]

    return transforms.Compose(transform_list)








def cloth_masking_with_grabcut(im_path, mask_folder, viz=False):
### Author: Matiur Rahman Minar ###
### EMCOM Lab, SeoulTech, 2021 ###
### Task: Generating binary mask/silhouette/segmentation ###
### especially for clothing image ###
### Focused method: GrabCut ###
    global faile_count
    lo = 250
    hi = 255

    img = cv2.imread(im_path, 0)
    # resize
    img = cv2.resize(img, (256, 192))
    # img1 = Image.open(im_path).convert('RGB')
    img2 = cv2.imread(im_path)
    img2 = cv2.resize(img2, (256, 192))
    img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2BGR)

    # 1. binary thresholding
    ret, th_bin = cv2.threshold(img, lo, hi, cv2.THRESH_BINARY_INV)

    # 2. Filling operation:

    # 2.1 Copy the thresholded image.
    im_floodfill = th_bin.copy()
    # 2.2 Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = th_bin.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    # 2.3 Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0, 0), 255);
    # 2.4 Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
    # 2.5 Combine the two images to get the foreground.
    th_filled = th_bin | im_floodfill_inv

    # 3. Morphology operation:
    kernel = np.ones((5, 5), np.uint8)

    # 3.1 opening for salt noise removal
    th_opened = cv2.morphologyEx(th_filled, cv2.MORPH_OPEN, kernel)

    # 3.2 closing for pepper noise removal (not needed it seems)
    # th_closed = cv2.morphologyEx(th_opened, cv2.MORPH_CLOSE, kernel)

    # 3.3 erosion for thinning out boundary
    # kernel = np.ones((3, 3), np.uint8)
    # th_eroded = cv2.erode(th_opened, kernel, iterations=1)

    # 4. GrabCut

    # 4.1 make mask
    # wherever it is marked white (sure foreground), change mask=1
    # wherever it is marked black (sure background), change mask=0
    gc_mask = np.zeros(img2.shape[:2], np.uint8)
    newmask = th_opened.copy()
    newmask_segm = cv2.bitwise_and(img2, img2, mask=newmask)

    # 4.2 define GrabCut priors
    absolute_foreground = cv2.erode(newmask, kernel, iterations=2)
    probable_foreground = newmask - absolute_foreground
    dilated_newmask = cv2.dilate(newmask, kernel, iterations=2)
    absolute_background = cv2.bitwise_not(dilated_newmask)
    probable_background = dilated_newmask - newmask

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # 4.3 change mask based on priors
    # any mask values greater than zero should be set to probable
    # foreground
    gc_mask[absolute_foreground > 0] = cv2.GC_FGD
    gc_mask[probable_foreground > 0] = cv2.GC_PR_FGD
    gc_mask[absolute_background > 0] = cv2.GC_BGD
    gc_mask[probable_background > 0] = cv2.GC_PR_BGD
    gc_prior = gc_mask.copy()

    # 4.4 apply GrabCut masking/segmentation
    try:
        gc_mask, bgdModel, fgdModel = cv2.grabCut(img2, gc_mask, None, bgdModel, fgdModel, 10, cv2.GC_INIT_WITH_MASK)
    except:
        print(" apply GrabCut masking/segmentation error:", im_path)
    gc_mask = np.where((gc_mask == 2) | (gc_mask == 0), 0, 1).astype('uint8')
    img2 = img2 * gc_mask[:, :, np.newaxis]



    # 6. save result
    gc_mask[gc_mask > 0] = 255    # make visible white
    # print("Saving ", mask_path)
    # mat_translation=np.float32([[1,0,-1],[0,1,-1]])
    # res= cv2.warpAffine(gc_mask,mat_translation,(w,h), borderValue=0)
    # res = cv2.resize(res, (190,254), interpolation=cv.INTER_NEAREST)
    # pad_img = cv2.copyMakeBorder(res, 0, bottom, left, right, cv2.BORDER_CONSTANT, value=[0,0,0]) #从图像边界向上,下,左,右扩的像素数目
    mask_saved_path = os.path.join(mask_folder, os.path.basename(im_path))
    cv2.imwrite(mask_saved_path, gc_mask)
    print("mask saved at: ",mask_saved_path)
    return mask_saved_path

# def main(each_list):
#     # Get paths
#     cloth_dir = "/home/belizabeth/zjk/PF/dataset/VITON_testdata/test_color/"
#     res_dir = "/home/belizabeth/zjk/PF/dataset/VITON_testdata/test_edge_GrabCut/"
    
#     # iterate images in the path
#     image_path = os.path.join(cloth_dir, each)
#     res_path = os.path.join(res_dir, each.replace(".jpg", ".png"))
#     cloth_masking_with_grabcut(image_path, res_path, viz=False)


if __name__ == "__main__":
    print("请不要直接运行mask裁剪器")

    # main(image_list[0])
    # from p_tqdm import p_map
    # _ = p_map(main, image_list)
    

