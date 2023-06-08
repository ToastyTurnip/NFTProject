import cv2
from PIL import Image
import numpy as np
import os

class ImageMaker:
    def __init__(self):
        self.imlist = list()
        self.pixels = np.ndarray(shape=[1080, 1920, 3], dtype="int")

    def _add_image(self, image, xysize, xycoord):
        #image preprocess - resize image
        if image.size != xysize:
            image = image.resize(xysize)

        self.imlist.append((xycoord, xysize))

        impixels = np.array(image)
        self.pixels[xycoord[0]:xycoord[0]+impixels.shape[0],xycoord[1]:xycoord[1]+impixels.shape[1]] = impixels
    
    def add_image_path(self, imagepath, xysize, xycoord):
        self._add_image(Image.open(imagepath), xysize, xycoord)

    def download(self):
        td = Image.fromarray(np.uint8(self.pixels))
        print(os.getcwd())
        td.save("output.png")


def test():
    imgpath = "saple.png"
    image = Image.open(imgpath)
    maker = ImageMaker()
    xysize = [200,200]
    xycoord = [0,0]

    maker._add_image(image, xysize, xycoord)

    maker.download()
    
    #cv2.imshow("Test", maker.pixels)

test()

# upload to ipfs: https://blog.thirdweb.com/guides/how-to-upload-and-pin-files-to-ipfs-using-storage/
