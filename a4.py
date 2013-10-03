#assignment 4 starter code
#by Abe Davis
#
# Student Name: Ryan Lacey
# MIT Email: rlacey@mit.edu

import numpy as np
import imageIO as io
from math import floor

############ HELPER FUNCTIONS############
def imIter(im):
    for y in xrange(im.shape[0]):
        for x in xrange(im.shape[1]):
            yield y, x

def analyzeNoise(imSeq):
    mean = imSeq[0].copy()
    squaredMean = imSeq[0].copy()**2
    N = len(imSeq)
    for i in xrange(1, N):
        mean += imSeq[i]
        squaredMean += imSeq[i]**2
    mean /= N
    squaredMean /= N
    variance = np.zeros(imSeq[0].shape)
    for i in xrange(N):
        diff = imSeq[i] - mean
        variance += diff*diff
    variance /= N-1
    return mean, variance, squaredMean
########## END HELPER FUNCTIONS ##########

def denoiseSeq(imageList):
    '''Takes a list of images, returns a denoised image
    '''
    return analyzeNoise(imageList)[0]

def logSNR(imageList, scale=1.0/20.0):
    '''takes a list of images and a scale. Returns an image showing log10(snr)*scale'''
    mean, variance, squaredMean = analyzeNoise(imageList)
    # Maringally shift all values to prevent divide by zero errors
    tolerance = 0.000000001
    squaredMean += tolerance
    variance += tolerance
    return np.log10(squaredMean / variance) * scale

def align(im1, im2, maxOffset=20):
    '''takes two images and a maxOffset. Returns the y, x offset that best aligns im2 to im1.'''
    minimumDifference = max(np.sum(im1)**2, np.sum(im2)**2)
    bestY = bestX = 0
    for y in range(-maxOffset, maxOffset):
        for x in range(-maxOffset, maxOffset):
            imRoll = np.roll(np.roll(im2, x, axis=1), y, axis=0)
            imDiffSq = np.sum((im1[maxOffset:-maxOffset, maxOffset:-maxOffset] - imRoll[maxOffset:-maxOffset, maxOffset:-maxOffset])**2)
            if imDiffSq < minimumDifference:
                minimumDifference = imDiffSq
                bestY = y
                bestX = x
    return bestY, bestX

def alignAndDenoise(imageList, maxOffset=20):
    '''takes a list of images and a max offset. Aligns all of the images to the first image in the list, and averages to denoise. Returns the denoised image.'''
    primary = imageList[0]
    alignedImgs = [primary]
    for img in imageList[1:]:
        offsetY, offsetX = align(primary, img, maxOffset)
        alignedImgs.append(np.roll(np.roll(img, offsetY, axis=0), offsetX, axis=1))
    return denoiseSeq(alignedImgs)

def basicGreen(raw, offset=0):
   '''takes a raw image and an offset. Returns the interpolated green channel of your image using the basic technique.'''
   (height, width) = np.shape(raw)
   out = raw.copy()
   for y in range(1, height-1):
       for x in range(1, width-1):
           if ((y+x+offset)% 2 == 0):
               out[y,x] = 0.25 * (raw[y-1, x] + raw[y+1, x] + raw[y, x-1] + raw[y, x+1])
   return out

def basicRorB(raw, offsetY, offsetX):
   '''takes a raw image and an offset in x and y. Returns the interpolated red or blue channel of your image using the basic technique.'''
   (height, width) = np.shape(raw)
   out = raw.copy()
   for y in range(1, height-1):
       for x in range(1, width-1):
        if((y-offsetY)%2==1 and (x-offsetX)%2==1):
            out[y,x] = 0.25 * (raw[y-1,x-1] + raw[y-1,x+1] + raw[y+1,x-1] + raw[y+1,x+1])
        elif((y-offsetY)%2==1 and (x-offsetX)%2==0):
            out[y,x] = 0.5 * (raw[y-1,x] + raw[y+1,x])
        elif((y-offsetY)%2==0 and (x-offsetX)%2==1):
            out[y,x] = 0.5 * (raw[y,x-1] + raw[y,x+1])
   return out

def basicDemosaic(raw, offsetGreen=0, offsetRedY=1, offsetRedX=1, offsetBlueY=0, offsetBlueX=0):
   '''takes a raw image and a bunch of offsets. Returns an rgb image computed with our basic techniche.'''
   (height, width) = np.shape(raw)
   out = np.zeros([height, width, 3])
   out[:,:,0] = basicRorB(raw, offsetRedY, offsetRedX)
   out[:,:,1] = basicGreen(raw, offsetGreen)
   out[:,:,2] = basicRorB(raw, offsetBlueY, offsetBlueX)
   return out

def edgeBasedGreen(raw, offset=1):
    '''same as basicGreen, but uses the edge based technique.'''
    (height, width) = np.shape(raw)
    out = raw.copy()
    for y in range(1, height-1):
        for x in range(1, width-1):
            if ((y+x+offset)%2 == 0):
                verticalDiff = abs(raw[y-1,x] - raw[y+1,x])
                horizontalDiff = abs(raw[y,x-1] - raw[y,x+1])
                if verticalDiff > horizontalDiff:
                    out[y,x] = 0.5 * (raw[y,x-1] + raw[y,x+1])
                else:
                    out[y,x] = 0.5 * (raw[y-1,x] + raw[y+1,x])
    return out

def edgeBasedGreenDemosaic(raw, offsetGreen=0, offsetRedY=1, offsetRedX=1, offsetBlueY=0, offsetBlueX=0):
    '''same as basicDemosaic except it uses the edge based technique to produce the green channel.'''
    (height, width) = np.shape(raw)
    out = np.zeros([height, width, 3])
    out[:,:,0] = basicRorB(raw, offsetRedY, offsetRedX)
    out[:,:,1] = edgeBasedGreen(raw, offsetGreen)
    out[:,:,2] = basicRorB(raw, offsetBlueY, offsetBlueX)
    return out


def greenBasedRorB(raw, green, offsetY, offsetX):
    '''Same as basicRorB but also takes an interpolated green channel and uses this channel to implement the green based technique.'''
    (height, width) = np.shape(raw)
    out = np.zeros([height, width])
    for y,x in imIter(raw):
        if ((x+offsetX)%2==0 and (y+offsetY)%2==0):
            out[y,x] = max(0, raw[y,x] - green[y,x])
    return green + basicRorB(out, offsetY, offsetX)


def improvedDemosaic(raw, offsetGreen=0, offsetRedY=1, offsetRedX=1, offsetBlueY=0, offsetBlueX=0):
    '''Same as basicDemosaic but uses edgeBasedGreen and greenBasedRorB.'''
    (height, width) = np.shape(raw)
    out = np.zeros([height, width, 3])
    green = edgeBasedGreen(raw, offsetGreen)
    out[:,:,0] = greenBasedRorB(raw, green, offsetRedY, offsetRedX)
    out[:,:,1] = green
    out[:,:,2] = greenBasedRorB(raw, green, offsetBlueY, offsetBlueX)
    return out


def split(raw):
    '''splits one of Sergei's images into a 3-channel image with height that is floor(height_of_raw/3.0). Returns the 3-channel image.'''
    (height_of_raw, width) = np.shape(raw)
    height = floor(height_of_raw/3.0)
    red = raw[:height]
    green = raw[height:2*height]
    blue = raw[2*height:3*height]
    out = np.zeros([height, width, 3])
    out[:,:,0] = red
    out[:,:,1] = green
    out[:,:,2] = blue
    return out

def sergeiRGB(raw, alignTo=1):
    '''Splits the raw image, then aligns two of the channels to the third. Returns the aligned color image.'''
    rgb = split(raw)
    (height, width, x) = np.shape(rgb)
    r = np.zeros([height, width])
    g = np.zeros([height, width])
    b = np.zeros([height, width])
    r[:,:] = rgb[:,:,0]
    g[:,:] = rgb[:,:,1]
    b[:,:] = rgb[:,:,2]
    (offsetYG, offsetXG) = align(b, g)
    rolledG = np.roll(np.roll(g, offsetYG, axis=0), offsetXG, axis=1)
    (offsetYR, offsetXR) = align(b, r)
    rolledR = np.roll(np.roll(r, offsetYR, axis=0), offsetXR, axis=1)
    out = np.zeros((height, width, 3))
    out[:,:,0] = b
    out[:,:,1] = rolledG
    out[:,:,2] = rolledR
    return out




























