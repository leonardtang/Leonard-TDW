import numpy as np
import os
import glob
import re
from PIL import Image

""" Converting from segmentation mask to bounding box """
""" Then cropping target object out of source image using bbox """


def get_bbox(seg_file, img_file):

    segmentation = np.load(seg_file)
    segmentation = np.asarray(segmentation)
    print("MASK SHAPE:", segmentation.shape)

    source_img = Image.open(img_file)
    source_img = np.asarray(source_img)
    print("IMG SHAPE:", source_img.shape)

    maskx = np.any(segmentation, axis=0)
    masky = np.any(segmentation, axis=1)
    # Top-left coordinates
    x1 = np.nonzero(maskx)[0][0]
    y1 = np.nonzero(masky)[0][0]
    # Bottom-right coordinates
    x2 = np.nonzero(maskx)[0][-1]
    y2 = np.nonzero(masky)[0][-1]
    print("Coordinates:", (x1, y1), (x2, y2))
    sub_image = source_img[y1:y2, x1:x2]w

    bbox_image = Image.fromarray(sub_image.astype('uint8'), 'RGB')
    bbox_image.save(os.path.splitext(seg_file)[0] + "_bbox.png")
    bbox_image.show()


full_img_list = glob.glob1(os.getcwd(), "img_*.png")
masks_list = glob.glob1(os.getcwd(), "*.npy")

for img_file in full_img_list:
    pattern = "img_(.*?).png"
    substring = re.search(pattern, img_file).group(1)
    for mask_file in masks_list:
        if re.search(substring, mask_file) is not None and re.search(substring, mask_file).group(0) in img_file:
            print("MASK FILE:", mask_file)
            get_bbox(mask_file, img_file)
