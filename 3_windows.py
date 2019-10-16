print(__doc__)

from time import time
import re
import numpy as np
import pandas as pd 
from numpy import genfromtxt
import collections, numpy
import os
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import NMF
import itertools


#================================================================================
#===CONFIG===

#Overlapping Frames
overlap = 10
frame_length = 30

dataRootPath = "./fps_10"
outputRootPath = "./output_Features_30_10_re"
debug=False

#================================================================================

#2 broken?
#["/half/Trial 2/2P1_F.csv", "/half/Trial 2/2P2_F.csv"],
#["/full/Trial 2/2P1_F.csv","/full/Trial 2/2P2_F.csv"]

halfFront = [["null","null"],
["null","null"],
["null","null"],
["/half/Trial 4/4P1_F.csv","/half/Trial 4/4P2_F.csv"], 
["/half/Trial 5/5P1_F.csv","/half/Trial 5/5P2_F.csv"],
["/half/Trial 6/6P1_F.csv","/half/Trial 6/6P2_F.csv"],
["/half/Trial 7/7P1_F.csv","/half/Trial 7/7P2_F.csv"],
["/half/Trial 8/8P1_F.csv","/half/Trial 8/8P2_F.csv"],
["null","null"],
["/half/Trial 10/10P1_F.csv", "/half/Trial 10/10P2_F.csv"],
["/half/Trial 11/11P1_F.csv","/half/Trial 11/11P2_F.csv"]]

halfBack = [["/half/Trial 1/1P1_B.csv", "/half/Trial 1/1P2_B.csv"],
["/half/Trial 2/2P1_B.csv", "/half/Trial 2/2P2_B.csv"],
["null","null"],
["/half/Trial 4/4P1_B.csv", "/half/Trial 4/4P2_B.csv"],
["/half/Trial 5/5P1_B.csv", "/half/Trial 5/5P2_B.csv"], 
["null","null"],
["/half/Trial 7/7P1_B.csv", "/half/Trial 7/7P2_B.csv"],
["/half/Trial 8/8P1_B.csv", "/half/Trial 8/8P2_B.csv"],  
["null","null"],
["/half/Trial 10/10P1_B.csv", "/half/Trial 10/10P2_B.csv"],
["/half/Trial 11/11P1_B.csv", "/half/Trial 11/11P2_B.csv"]]

fullFront = [["null","null"],
["null","null"],
["null","null"],
["/full/Trial 4/4P1_F.csv","/full/Trial 4/4P2_F.csv"],
["/full/Trial 5/5P1_F.csv","/full/Trial 5/5P2_F.csv"],
["/full/Trial 6/6P1_F.csv","/full/Trial 6/6P2_F.csv"],
["/full/Trial 7/7P1_F.csv","/full/Trial 7/7P2_F.csv"],
["/full/Trial 8/8P1_F.csv","/full/Trial 8/8P2_F.csv"],
["/full/Trial 9/9P1_F.csv","/full/Trial 9/9P2_F.csv"],
["/full/Trial 10/10P1_F.csv","/full/Trial 10/10P2_F.csv"],
["/full/Trial 11/11P1_F.csv","/full/Trial 11/11P2_F.csv"]]

fullBack = [["/full/Trial 1/1P1_B.csv","/full/Trial 1/1P2_B.csv"],
["/full/Trial 2/2P1_B.csv","/full/Trial 2/2P2_B.csv"],
["null","null"],
["/full/Trial 4/4P1_B.csv","/full/Trial 4/4P2_B.csv"],
["/full/Trial 5/5P1_B.csv","/full/Trial 5/5P2_B.csv"],
["/full/Trial 6/6P1_B.csv","/full/Trial 6/6P2_B.csv"],
["/full/Trial 7/7P1_B.csv","/full/Trial 7/7P2_B.csv"],
["/full/Trial 8/8P1_B.csv","/full/Trial 8/8P2_B.csv"],
["/full/Trial 9/9P1_B.csv","/full/Trial 9/9P2_B.csv"],
["/full/Trial 10/10P1_B.csv","/full/Trial 10/10P2_B.csv"],
["/full/Trial 11/11P1_B.csv","/full/Trial 11/11P2_B.csv"]]




#read csv file in Numpy array
#usecols can be used to get specific columns:  usecols = 0, 1, 3,9
def read_csv(fileName):
    print("in the function: ", fileName)
    data = np.genfromtxt(fileName, delimiter=',', skip_header=2, dtype ='unicode')
    return data

#get frame number form first column 
def get_frame_number(data, n_rows):
    rx = "_(\d{5,})_"
    for i in range(0, n_rows):
        firstCol = data[i,0]
        frameId = re.search(rx,firstCol)
        data[i,0] = frameId[1]
    

#sort Numpy array by first column
def sort_by_column(data):
    #sortedArr = data[data[:,0].argsort()]
    sortedArr = np.sort(data, axis=0) 
    return sortedArr


#get first column
def get_column(data, col):
    col_data = data [:,col]
    return col_data
    

def dup_cols(a, indx, num_dups=1):
    return np.insert(a,[indx+1]*num_dups,a[:,[indx]],axis=1)
                
                
def checkPoint(pnt):
    for i in range(len(pnt)):
        if (pnt[i] != -1):
            return True
    return False                
                            
def create_windows(filtered_data, overlap, size):
    
    s_idx=0
    e_idx=size

    cluster_points = []
    cluster_frames = []
    cluster_assoc = dict()


    while (e_idx<len(filtered_data)):
        emptyCount = 0
        point = []
        last_point = []
        current_frame_range = [filtered_data[s_idx][0], filtered_data[e_idx][1], filtered_data[s_idx][2]]        
        for mi in range(s_idx, e_idx):
            if(checkPoint(filtered_data[mi][3:])):
                point = [*point, *filtered_data[mi,3:]]
                last_point = filtered_data[mi,3:]
                current_frame = filtered_data[mi,0:3]
            else:
                emptyCount += 1
                if(len(point)>0):
                    #point = np.append(point, point[-1])
                    point = [*point, *last_point]
                else:
                    #EMPTY FIRST POINT - WHAT DO?
                    print ("Dropping window with empty first ", emptyCount, " in ", s_idx, " - ", e_idx)    
                    break
        
        if(emptyCount < size/2) and (len(point)>0):            
            cluster_points.append(numpy.array(point).astype(np.float64))
            cluster_frames.append(current_frame_range)
        else:
            print ("Skipping window, empty count ", emptyCount, " in ", s_idx, " - ", e_idx)    
        
        s_idx += overlap
        e_idx += overlap        

    return cluster_points, cluster_frames
    
    
    
def getFromFile(fileName):
  #Grab config data from first line
  print(fileName)
  config = np.genfromtxt(fileName, delimiter=',', usecols = range(0,3), max_rows =1)
  header = np.genfromtxt(fileName, delimiter=',', skip_header=1, max_rows =1, dtype ='unicode')

  #read the rest of the feature data 
  pose_data = read_csv(fileName)
  n_rows, n_columns = pose_data.shape
  print(" \t n_samples %d, \t n_features %d"
        % (n_rows, n_columns))
  


  #duplicated framename and trial
  #base_data = dup_cols(pose_data, 0)
  #strip first collumn to have just the frame number
  #get_frame_number(base_data, n_rows)
  #sort posedata by first frame number
  #sorted_pose_data = sort_by_column(base_data)

  #print("Fps = ", fps, " rate = ", frame_divider, " No samples expected = ", ((n_rows/fps)))  
  
  #filtered_data = filter_to_fps(frames_per_second, fileName, sorted_pose_data, header)
  
  #print("Filtered Data ", len(filtered_data))  
  
  cluster_points, cluster_frames  = create_windows(pose_data, overlap, frame_length)
  
  print ("Resulting in ", len(cluster_points), " windows")
  
  return config, cluster_points, cluster_frames

    
def frameStack(fsp, aData, aFrames, bData, bFrames):
    skipCount = 0
    outputData = []
    
    #sanity check:
    print("Something is strange!", len(aData), len(aFrames), len(bData), len(bFrames))
    
    if(not (len(aData) == len(aFrames) == len(bData) == len(bFrames))):
        print("Something is strange!", len(aData), len(aFrames), len(bData), len(bFrames))
        #return outputData
    stopper = len(bFrames) if len(aFrames)>len(bFrames) else len(aFrames)
    
    for i in range(0,stopper):
        if(aFrames[i][0] == bFrames[i][0]):
            outputData.append([*aFrames[i], *aData[i], *bData[i]])
        else:
            skipCount +=1
            if(skipCount<10):
                print("missmatch in frames:", aFrames[i], " - ", bFrames[i])

    print("Skip missmatching frames:", skipCount)
    return outputData
        
    


for trialFiles in itertools.chain(fullFront, halfFront):

  fileName = trialFiles[0]
  if(fileName == "null"):
    #skip the null trials in the list
    continue

 
  if (not os.path.exists(dataRootPath+trialFiles[0])) or (not os.path.exists(dataRootPath+trialFiles[1])):
      print("Input File Not Found:", dataRootPath + fileName)
      continue
  
  outFile = fileName.replace('/', '_')[1:]
  print (outFile)
  
  aConfig, aPoints, aFrames = getFromFile(dataRootPath+trialFiles[0])
  bConfig, bPoints, bFrames = getFromFile(dataRootPath+trialFiles[1])
  fsp_column = [aConfig[2]] * len(aFrames)
  #numpy array of framesnames and data
  print("Shape Check:", len(aFrames), " - ",len(fsp_column), " - Apoints: ",len(aPoints), " - BPoints: ",len(bPoints), " - aFrames: ", len(aFrames), " - bFrames: ",len(bFrames))
  
  #print(bFrames[0:20])
  
  
  if debug == True: #Output assoc toggle 
      if not os.path.exists(outputRootPath+"/framea/"):
          os.makedirs(outputRootPath+"/framea/")
      pd.DataFrame(aFrames).to_csv(outputRootPath+"/framea/"+outFile)

      if not os.path.exists(outputRootPath+"/frameb/"):
          os.makedirs(outputRootPath+"/frameb/")
      pd.DataFrame(bFrames).to_csv(outputRootPath+"/frameb/"+outFile)

  
  #full_output_data = np.column_stack((aFrames,fsp_column,aPoints,bPoints))
  full_output_data = frameStack(aConfig[2], aPoints, aFrames, bPoints, bFrames)
  
  #print (full_output_data)
  
  print("Checking zipped data: ", len(full_output_data))
  
  if not os.path.exists(outputRootPath+"/"):
      os.makedirs(outputRootPath+"/")


  #store Numpy array 'labeled data' in csv file
  pd.DataFrame(full_output_data).to_csv(outputRootPath+"/"+outFile)


    








