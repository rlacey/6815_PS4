#script for running/testing assignment 4
#Starter code by Abe Davis
#
#
# Student Name: Ryan Lacey
# MIT Email: rlacey@mit.edu

import a4
import numpy as np
import glob
import imageIO as io

io.baseInputPath = './'

def getPNGsInDir(path):
    fnames = glob.glob(path+"*.png")
    pngs = list()
    for f in fnames:
        #print f
        imi = io.getImage(f)
        pngs.append(imi)
    return pngs

def getRawPNGsInDir(path):
    fnames = glob.glob(path+"*.png")
    pngs = list()
    pngnames = list()
    print path
    for f in fnames:
        print f
        imi = io.imreadGrey(f)
        pngs.append(imi)
        pngnames.append(f)
    return pngs, pngnames

def getFirstN(imList, N):
    '''Super simple function. I'm only including it as a reminder that you can test on a subset of the data. Python is slow...'''
    return imList[:N]

def testDenoise(imageList, outputname):
    #denoise
    imdenoise = a4.denoiseSeq(imageList)
    io.imwrite(imdenoise, str(outputname+'_denoise_x%03d'%(len(imageList)))+".png")

def testSNR(imageList, outputname):
    #SNR
    imSNR = a4.logSNR(imageList)
    io.imwrite(imSNR, str(outputname+'_logSNR_x%03d'%(len(imageList)))+".png")

def testAlign():
    print 'Testing Align'
    align1 = np.zeros([50,50,3])
    align2 = np.zeros([50,50,3])
    align1[10,10] = 1
    align2[13,11] = 1
    print 'We recommend creating a simple test case for testAlign() here. Meybe set one pixel of each image to be 1?'
    yalign, xalign = a4.align(align1, align2, 5)
    yalign2, xalign2 = a4.align(align2, align1, 5)
    print "alignment 1->2 is:"+'[{},{}]'.format(yalign, xalign)
    print "alignment 2->1 is:"+'[{},{}]'.format(yalign2, xalign2)


def testAlignAndDenoise(imageList, outputname):
    imADN = a4.alignAndDenoise(imageList)
    io.imwrite(imADN, str(outputname+'_ADN_x%03d'%(len(imageList)))+".png")

def testBasicGreenz(raw, outputname, offset=1):
    rout = a4.basicGreen(raw, offset)
    io.imwrite(rout, outputname+'_basicGreen.png')


def testBasicDemosaic(raw, outputname, gos =1, rosy=1,rosx=1,bosy=0,bosx=0):
    rout = a4.basicDemosaic(raw, gos, rosy, rosx, bosy, bosx)
    io.imwrite(rout, outputname+'_basicDemosaic.png')

def testEdgeBasedGreenDemosaic(raw, outputname, gos =1, rosy=1,rosx=1,bosy=0,bosx=0):
   rout = a4.edgeBasedGreenDemosaic(raw, gos, rosy, rosx, bosy, bosx)
   io.imwrite(rout, outputname+'_edgeBasedGreenDemosaic.png')

def testImprovedDemosaic(raw, outputname, gos =1, rosy=1,rosx=1,bosy=0,bosx=0):
    rout = a4.improvedDemosaic(raw, gos, rosy, rosx, bosy, bosx)
    io.imwrite(rout, outputname+'_improvedDemosaic.png')

def testSergei():
    sergeis, sergeiNames = getRawPNGsInDir("data/Sergei/")
    scount = 0
    for f in sergeis:
        io.imwrite(a4.sergeiRGB(f), str('Sergei'+'%03d'%(scount))+'.png')
        scount = scount +1

testDenoise(getPNGsInDir('data/aligned-ISO400/'), 'ISO400-denoise')
testDenoise(getPNGsInDir('data/aligned-ISO3200/'), 'ISO3200-denoise')
testSNR(getPNGsInDir('data/aligned-ISO400/'), 'ISO400-SNR')
testSNR(getPNGsInDir('data/aligned-ISO3200/'), 'ISO3200-SNR')
testAlign()
testAlignAndDenoise(getPNGsInDir("data/green/"), 'green-aligned-full')
testBasicGreenz(io.imreadGrey("data/raw/signs-small.png"), 'demo')
testBasicDemosaic(io.imreadGrey("data/raw/signs-small.png"), 'sign-small', gos =0, rosy=1,rosx=1,bosy=0,bosx=0)
testEdgeBasedGreenDemosaic(io.imreadGrey("data/raw/signs-small.png"), 'sign-small', gos =0, rosy=1,rosx=1,bosy=0,bosx=0)
testImprovedDemosaic(io.imreadGrey("data/raw/signs-small.png"), 'sign-small2', gos =0, rosy=1,rosx=1,bosy=0,bosx=0)
testSergei()