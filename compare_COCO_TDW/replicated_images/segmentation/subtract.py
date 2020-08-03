import glob
import os
import re
import numpy as np
from PIL import Image

# Subtract masks: mask2 - mask1
mask_list = glob.glob1(os.getcwd(), "*.npy")
mask_counts = len(mask_list)
subtracted_masks = [None] * (mask_counts - 1)

for i, file1 in enumerate(mask_list[:-1]):
    file2 = mask_list[i+1]
    file_ending1 = int(re.search(r'\d+', file1).group())
    file_ending2 = int(re.search(r'\d+', file2).group())
    if file_ending2 < file_ending1:
        continue
    mask1 = np.load(file1)
    mask2 = np.load(file2)
    subtracted = mask2 - mask1
    # print(subtracted)
    image = Image.fromarray(subtracted)
    image.save("subtracted_{}.png".format(i))
    # image.show()
    # Cannot update masks until all masks have been subtracted
    subtracted_masks[i] = subtracted

for i, file_name in enumerate(mask_list):
    # Keep first (one object) mask
    if i > 0:
        np.save(file_name, subtracted_masks[i - 1])

