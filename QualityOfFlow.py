from dataReader import dataReader
from qualityAnalysis import  qualityAnalysis
import cv2
import numpy as np
from numpy import linalg as LA
import getpass
from utils import flow2motion

_temp = __import__("flownet2-pytorch.utils.flow_utils", globals(), locals(), ['flow2img', 'readFlow'], 0)
flow2img = _temp.flow2img
readFlow = _temp.readFlow


def findMag(du, dv):
    max_flow = np.abs(max(np.max(du), np.max(dv)))
    mag = np.sqrt(du * du + dv * dv) * 8 / max_flow 
    return mag

def magToImg(mag):
    mag = np.float32(mag)
    return cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


# main path of data
path = '../Desktop/dataset/PTZ/zoomInZoomOut/'
if getpass.getuser() == 'ibrahim':
    path = '../Desktop/Dataset/Change Detection Dataset/dataset2014/dataset/PTZ/continuousPan/'

roiName = 'ROI.bmp'

f = open(path+"temporalROI.txt", "r")
line = f.readline()
temporalRoiFirst, temporalRoiLast = [int(i) for i in line.split()]
f.close()

# reading input and groundtruth files
dr = dataReader()
imageFiles = dr.readFiles(str(path)+'input', 'jpg')
groundTruthFiles = dr.readFiles(str(path)+'groundtruth', ".png")
flowFiles = dr.readFiles(path+'flow', 'flo')


roi = cv2.imread(str(path)+'ROI.bmp')
binaryRoi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

qa = qualityAnalysis()

step = 8
imgPrev = None
isStopped = False
i = temporalRoiFirst-1
processedFrameCounter = 0
while i < temporalRoiLast:
    
    keyy = cv2.waitKey(10)
    if  keyy == ord('q'):
        break

    if keyy == ord('s'):
        isStopped = ~isStopped

    if isStopped:
        continue
    
    img = cv2.imread(imageFiles[i])
    groundTruth = cv2.imread(groundTruthFiles[i])
    flow = readFlow(flowFiles[i-step])


    groundTruth = cv2.cvtColor(groundTruth, cv2.COLOR_BGR2GRAY)

    i +=1
    if groundTruth[0,0] == 170:
        continue

    print(i)
    groundTruth = np.multiply(groundTruth, binaryRoi)
    groundTruth[groundTruth>0] = 1

    

    motion = flow2motion(flow)
    cv2.imshow("motion", motion)

    img[motion > 0, 2] = 255

    motion = np.multiply(motion, binaryRoi)
    motion[motion>0] = 1
    
    # qa.compare(groundTruth, motion)
    processedFrameCounter +=1
    # print(qa.printIterationResults())


    cv2.imshow("img", img)
    # cv2.imshow("gt", groundTruth*255)
    cv2.imshow("flow", flow2img(flow))


print("processedFrameCounter: ", processedFrameCounter)
print("\n ***Mean values*** \n ")
print(qa.results(path))
