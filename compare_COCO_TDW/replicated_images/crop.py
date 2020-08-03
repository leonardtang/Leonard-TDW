import sys
import numpy as np
from PIL import Image

""" Format: python3 crop.py segmentation_mask source_image """

if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("ERROR: Please format as python3 crop.py numpy_mask single_object_src_IMG ")
    sys.exit(1)

mask_file = sys.argv[1]
source_image = sys.argv[2]
image = Image.open(source_image)
image = np.asarray(image)
mask = np.load(mask_file)
mask = np.stack((mask,)*3, axis=-1)
print(mask.shape)
print(image.shape)
# print(mask)
cropped = np.multiply(mask, image)
cropped = cropped.astype(np.uint8)
print(cropped.dtype)
cr_img = Image.fromarray(cropped)
cr_img.save(mask_file[:-13] + "_cropped.png")
cr_img.show()


