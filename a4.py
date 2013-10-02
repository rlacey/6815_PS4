#assignment 4 starter code
#by Abe Davis
#
# Student Name: Ryan Lacey
# MIT Email: rlacey@mit.edu

import numpy as np
import imageIO as io

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
    for y in range(maxOffset+1):
        imRoll = np.roll(im2, y, axis=0)
        for x in range(maxOffset+1):
            imRoll = np.roll(imRoll, 1, axis=1)
            imDiffSq = np.sum((im1[maxOffset:-maxOffset] - imRoll[maxOffset:-maxOffset])**2)
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

##def basicGreen(raw, offset=1):
##    '''takes a raw image and an offset. Returns the interpolated green channel of your image using the basic technique.'''    
####    out = np.zeros([height-2, width-2])
####    for y,x in imIter(out):        
####        yp = y+1
####        xp = x+1
####        if (yp + xp + offset) % 2 == 1:
####            # out = avg(top, bottom, left, right)
####            out[y,x] = 0.25 * (raw[yp-1, xp] + raw[yp+1, xp] + raw[yp, xp-1] + raw[yp, xp+1])
####        else:
####            out[y,x] = raw[y,x]
##    (height, width) = np.shape(raw)
##    out = raw.copy()
##    for y in range(1, height-1):
##        for x in range(1, width-1):
##            if (y + x + offset) % 2 == 1:
##                out[y,x] = 0.25 * (raw[y-1, x] + raw[y+1, x] + raw[y, x-1] + raw[y, x+1])
##    return out
##
##
##def basicRorB(raw, offsetY, offsetX):
##    '''takes a raw image and an offset in x and y. Returns the interpolated red or blue channel of your image using the basic technique.'''
##    (height, width) = np.shape(raw)    
##    out = raw.copy()
##    for y in range(1, height-1):
##        for x in range(1, width-1):
##            if (x + offsetX) % 2 == 0:
##                if (y + offsetY) == 1:
##                    out[y,x] = 0.5 * (raw[y-1, x] + raw[y+1, x])
##            else:
##                if (y + offsetY) % 2 == 0:
##                    out[y,x] = 0.5 * (raw[y, x-1] + raw[y, x+1])
##                else:
##                    out[y,x] = 0.25 * (raw[y-1, x-1] + raw[y-1, x+1] + raw[y+1, x-1] + raw[y+1, x+1])
##    return out
##                    
##
##def basicDemosaic(raw, offsetGreen=0, offsetRedY=1, offsetRedX=1, offsetBlueY=0, offsetBlueX=0):
##    '''takes a raw image and a bunch of offsets. Returns an rgb image computed with our basic techniche.'''
##    out = np.zeros((raw.shape[0], raw.shape[1], 3))
##    out[:,:,0] = basicRorB(raw, offsetRedY, offsetRedX)
##    out[:,:,1] = basicGreen(raw, offsetGreen)
##    out[:,:,2] = basicRorB(raw, offsetBlueY, offsetBlueX)
##    return out    

def basicGreen(raw, offset=1):
    '''takes a raw image and an offset. Returns the interpolated green channel of your image using the basic technique.'''
    out = np.zeros((raw.shape[0] - 2, raw.shape[1] - 2))
    for y, x in imIter(out):
        yorig, xorig = (y+1, x+1)
        if (xorig + yorig + offset) % 2 == 0:
            out[y, x] = raw[yorig, xorig]
        else:
            out[y, x] = 0.25 * (raw[yorig+1, xorig] + raw[yorig-1, xorig] + raw[yorig, xorig+1] + raw[yorig, xorig-1])
    return out

def basicRorB(raw, offsetY, offsetX):
    '''takes a raw image and an offset in x and y. Returns the interpolated red or blue channel of your image using the basic technique.'''
    out = np.zeros((raw.shape[0] - 2, raw.shape[1] - 2))
    for y, x in imIter(out):
        yorig, xorig = (y+1, x+1)
        if (xorig + offsetX) % 2 == 0:
            if (yorig + offsetY) % 2 == 0:
                out[y, x] = raw[yorig, xorig]
            else:
                out[y, x] = 0.5 * (raw[yorig-1, xorig] + raw[yorig+1, xorig])
        else:
            if (yorig + offsetY) % 2 == 0:
                out[y, x] = 0.5 * (raw[yorig, xorig-1] + raw[yorig, xorig + 1])
            else:
                out[y, x] = 0.25 * (raw[yorig+1, xorig+1] + raw[yorig-1, xorig+1] + raw[yorig+1, xorig-1] + raw[yorig-1, xorig-1])
    return out

def basicDemosaic(raw, offsetGreen=0, offsetRedY=1, offsetRedX=1, offsetBlueY=0, offsetBlueX=0):
    '''takes a raw image and a bunch of offsets. Returns an rgb image computed with our basic techniche.'''
    out = np.zeros((raw.shape[0] - 2, raw.shape[1] - 2, 3))
    out[:,:,0] = basicRorB(raw, offsetRedY, offsetRedX)
    out[:,:,1] = basicGreen(raw, offsetGreen)
    out[:,:,2] = basicRorB(raw, offsetBlueY, offsetBlueX)
    return out

def edgeBasedGreenDemosaic(raw, offsetGreen=0, offsetRedY=1, offsetRedX=1, offsetBlueY=0, offsetBlueX=0):
    '''same as basicDemosaic except it uses the edge based technique to produce the green channel.'''

def edgeBasedGreen(raw, offset=1):
    '''same as basicGreen, but uses the edge based technique.'''
    #out =raw.copy()
    

def greenBasedRorB(raw, green, offsetY, offsetX):
    '''Same as basicRorB but also takes an interpolated green channel and uses this channel to implement the green based technique.'''
    #out =raw.copy()

def improvedDemosaic(raw, offsetGreen=0, offsetRedY=1, offsetRedX=1, offsetBlueY=0, offsetBlueX=0):
    '''Same as basicDemosaic but uses edgeBasedGreen and greenBasedRorB.'''


def split(raw):
    '''splits one of Sergei's images into a 3-channel image with height that is floor(height_of_raw/3.0). Returns the 3-channel image.'''

def sergeiRGB(raw, alignTo=1):
    '''Splits the raw image, then aligns two of the channels to the third. Returns the aligned color image.'''
