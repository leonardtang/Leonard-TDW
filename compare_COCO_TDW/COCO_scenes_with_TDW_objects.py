from pycocotools.coco import COCO
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
import pylab
import os
from os import path
import shutil
import csv

COCO_to_TDW_csv = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/objects_changing_positions/COCO_to_TDW.csv"
COCO_to_TDW = {}
with open(COCO_to_TDW_csv) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        COCO_to_TDW[row[0]] = row[1]

COCO_categories_csv = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/COCO_categories.csv"
COCO_categories = []
with open(COCO_categories_csv) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        COCO_categories.append(row[0])


def get_compatible_scene_imgs(categories=None):
    """ Get all possible TDW-compatible scenes from val/test set """

    if categories is None:
        category_Ids = []

    dataDir = '/Users/leonard/Desktop/coco'
    dataType = 'val2014'
    annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)

    coco = COCO(annFile)
    category_Ids = coco.getCatIds(catNms=categories)
    imgIds = coco.getImgIds(catIds=category_Ids)  # All possible images matching criteria
    compatible_scene_imgs = []

    for i, ID in enumerate(imgIds):
        all_TDW_objects = True
        img = coco.loadImgs(ID)[0]
        annIds = coco.getAnnIds(imgIds=img['id'], iscrowd=None)
        anns = coco.loadAnns(annIds)
        for ann in anns:
            if ann['category_id'] > 80:
                break
            if COCO_categories[ann['category_id'] - 1] not in COCO_to_TDW.keys():
                all_TDW_objects = False
                break

        if all_TDW_objects:
            print(img['coco_url'])
            print(anns)
            # anns_img = np.zeros((img['height'], img['width']))
            # for ann in anns:
            #     anns_img = np.maximum(anns_img, coco.annToMask(ann) * ann['category_id'])
            # I = io.imread(img['coco_url'])
            # plt.axis('off')
            # plt.imshow(anns_img)
            # plt.imshow(I)
            # plt.show()
            # Close plt each time / update plt
            # coco.showAnns(anns)
            compatible_scene_imgs.append(img)

    return compatible_scene_imgs


def move_files(source_path, destination, file_list):
    """ Moving compatible files from folder to another """
    src = source_path
    dst = destination

    files = [i for i in os.listdir(src) if path.isfile(path.join(src, i)) and i in file_list]
    for f in files:
        shutil.copy(path.join(src, f), dst)


images = get_compatible_scene_imgs(["traffic light"])
file_names = []
max_images = 100
for i, image in enumerate(images):
    if i >= max_images:
        break
    file_names.append(image["file_name"])

file_names.sort()
print(len(file_names))

with open('compatible_scenes.csv', mode='w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for file in file_names:
        writer.writerow(file)

move_files("/Users/leonard/Desktop/coco/images/val2014", "/Users/leonard/Desktop/coco/images/to_replicate/traffic_light", file_names)

# col_dir = '/Users/leonard/Desktop/coco/images/to_replicate/*.jpg'
# col = io.imread_collection(col_dir)
# for image in col:
# 
# print(col)
