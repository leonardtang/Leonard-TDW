from PIL import Image
import numpy as np
import sys
import os

# Format: python3 masks.py file_name
if len(sys.argv) < 2 or len(sys.argv) > 2:
    print("ERROR: Please format as python3 masks.py single_object_src_ID ")
    sys.exit(1)
file_name = sys.argv[1]
image = Image.open(file_name)
pixels = np.asarray(image)
image = Image.fromarray(pixels)
# image.show()
# print(pixels)
np.save(os.path.splitext(file_name)[0], pixels)
