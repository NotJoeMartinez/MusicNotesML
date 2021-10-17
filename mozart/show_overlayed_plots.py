
from os import access
from cv2 import log, imread
import skimage.io as io
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.pyplot import bar
import numpy as np
from skimage.exposure import histogram
from skimage.color import rgb2gray
from skimage.filters import threshold_otsu, gaussian, median
from skimage.morphology import binary_opening, binary_closing, binary_dilation, binary_erosion, closing, opening, square, skeletonize, disk
from skimage.feature import canny
from skimage.transform import resize


def show_og_overlayed(og_fname, ov_fname, res):
    rows = 3
    columns = 1
    og = imread(og_fname)
    ov = imread(ov_fname)
    fig = plt.figure(figsize=(10, 7))

    fig.add_subplot(rows, columns, 1)

    # show og img 
    plt.imshow(ov)
    plt.title("With Overlay")
    fig.add_subplot(rows, columns, 2)

    # show overlayed img 
    plt.imshow(og)
    plt.title("Original Image")


    fig.add_subplot(rows, columns, 3)
    plt.axis("off")
    plt.title("Output array of notes")
    plt.text(0, 0.8, str(res))

    plt.show()

