from PIL import Image
import numpy as np
import sys

# Format: python3 masks.py file_name
file_name = sys.argv[1]
image = Image.open(file_name).convert('L')
pixels = np.asarray(image)
pixels = np.where(pixels > 0.001, 1, 0)
np.save(file_name + '_mask', pixels)
print(pixels.shape)
print(pixels)
