from pycocotools.coco import COCO
from sklearn.model_selection import train_test_split
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pylab


def calculate_matrix():
    """ Calculating co-occurrence matrix, normalized by each row """

    pylab.rcParams['figure.figsize'] = (8.0, 10.0)
    dataDir = "/Users/leonard/Desktop/coco"
    dataType = 'train2014'
    annTrainFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
    coco = COCO(annTrainFile)

    # Getting object categories
    cats = coco.loadCats(coco.getCatIds())
    nms = [cat['name'] for cat in cats]
    # print(nms)
    # print(len(nms))

    # Writing list of COCO categories to csv
    with open('COCO_categories.csv', 'w') as f:
        for cat in nms:
            f.write("%s\n" % cat)

    # Splitting entire image data set into training/testing data
    # Note these are just the images (input) -- no labels included
    # Random state ensures the same seed each time
    imgIds = coco.getImgIds()
    train_img, val_img = train_test_split(imgIds, test_size=0.2, random_state=0)
    # print("Train Length:", len(train_img), "Image Ids:", train_img)
    # print("Val Length:", len(val_img), "Image IDs:", val_img)

    co_occurrence = np.zeros((80, 80), dtype=float)
    # Double for loop approach -- maybe flawed, could have multiple object instances in a single image
    for i, category_1 in enumerate(nms):
        catId_1 = coco.getCatIds(catNms=[category_1])
        imgIds_1 = coco.getImgIds(catIds=catId_1)
        for j, category_2 in enumerate(nms):
            if j > i:
                break
            catId_2 = coco.getCatIds(catNms=[category_2])
            imgIds_2 = coco.getImgIds(catIds=catId_2)
            # These images contain BOTH required classes
            co_occur = len(set(imgIds_1) & set(imgIds_2) & set(train_img))
            # Counts of co_occurrence normalized by total training image counts
            co_occurrence[i, j] = co_occurrence[j, i] = co_occur
            # len(set(imgIds_1).union(set(imgIds_2 & (set(train_img)))

    # Normalize such that sum across row = 1 (note: not symmetric now)
    for i in range(80):
        # Sum across each row of co_occurrence matrix
        row_total = np.sum(co_occurrence[i, :])
        # Normalize by total number of images in each row (instances of each object)
        co_occurrence[i, :] /= row_total

    # print(co_occurrence)
    # Sanity check
    # print(np.sum(co_occurrence[0, :]))
    # print(np.sum(co_occurrence[:, 0]))

    return [co_occurrence, nms]


def plot_heatmap():
    """ Plot heatmap; get matrix and nms from calculate_matrix() """
    [matrix, nms] = calculate_matrix()
    # Convert numpy 2Darray to DataFrame
    co_occurrence_df = pd.DataFrame(matrix)
    sns.set()
    ax = sns.heatmap(co_occurrence_df, xticklabels=nms, yticklabels=nms)
    ax.xaxis.tick_top()
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    plt.rc('font', size=6)
    plt.show()


def get_max_co_occurrence(max_rows, num_appear):
    """ Get a matrix of max_rows (# of possible object combinations) corresponding
        to num_appear columns (# of desired co-occurring objects in scene) """

    # Getting co_occurrence and nms from calculate_matrix()
    [matrix, nms] = calculate_matrix()
    # Max number of rows (top n viable combinations of objects)
    max_rows = max_rows
    # Stores number of objects to appear in scene
    num_appear = num_appear
    # Stores all rows' co_occurrence sums
    rows_to_co_occur = {}

    for i in range(len(matrix)):
        # Removing i index (since this is repeated object)
        row_to_sort = np.concatenate([-matrix[i][0:i], -matrix[i][i+1:]])
        temp = np.partition(row_to_sort, num_appear)
        # Largest n correlated category values for this object
        row_n_max = -temp[:num_appear]
        # Summing up each row's co_occurrence values
        row_co_occur_sum = np.sum(row_n_max)
        rows_to_co_occur[i] = row_co_occur_sum

    # Sort dictionary by descending values (co_occurrence values)
    rows_to_co_occur = {k: v for k, v in sorted(rows_to_co_occur.items(),
                                                key=lambda item: item[1],
                                                reverse=True)}

    # Matrix that stores indices of n max rows with largest correlations
    max_n_row_categories = np.array(range(max_rows * num_appear), dtype='a5').reshape((max_rows, num_appear))
    max_n_row_categories = max_n_row_categories.astype('U256')
    # Get "max_rows" number of rows corresponding to "num_appear" correlated objects
    for i, keys in enumerate(rows_to_co_occur.keys()):
        if i >= max_rows:
            break
        indices = np.argpartition(-matrix[keys], num_appear)
        indices = indices[:num_appear]
        for j in range(len(indices)):
            max_n_row_categories[i][j] = nms[indices[j]]

    # Might not line up with raw total counts, as each object (row) is normalized by only the number of times it appears
    # Conditional P(Co-Occurring Object | Row Object)
    # Row object appears in the first column of the resulting matrix
    return max_n_row_categories


# print("Highest co-occurring objects: \n", get_max_co_occurrence(co_occurrence, max_rows=10, num_appear=30))

if __name__ == "__main__":
    print(get_max_co_occurrence(5, 30))



