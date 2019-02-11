import matplotlib.pyplot as plt
import numpy as np
import statistics as sts
from skimage import io

def cinz(pixel):

        soma= pixel[0]
        
        return soma/255


rgb = io.imread("test3.jpg")


grey = [ [ cinz(pixel) for pixel in linha]  for linha in rgb]

fig = plt.imshow(grey, cmap ="gray")

fig.axes.get_xaxis().set_visible(False)
fig.axes.get_yaxis().set_visible(False)

grey_1d = []
for linha in grey:
        grey_1d += linha
"""      
f, axarr = plt.subplots(1,2)

axarr[1].imshow(grey, cmap ="gray")

axarr[0].hist(grey_1d, bins = 40)"""

plt.savefig("nirgray_nofilter.jpg")