import os
import sys
import datetime
import imageio
import matplotlib
import cv2
import numpy as np
from os.path import isfile, join
from IPython.display import HTML
import io
import base64
import csv
from getpass import getpass
import shutil
import re
from pandas import DataFrame, read_csv
import pandas as pd 
import itertools

#get frame number form first column 
def get_frame_number(data, n_rows):
    rx = "_(\d{5,})_"
    for i in range(0, n_rows):
        firstCol = data[i,0]
        frameId = re.findall(rx,firstCol)
        data[i,0] = frameId[0]
        
def dup_cols(a, indx, num_dups=1):
    return np.insert(a,[indx+1]*num_dups,a[:,[indx]],axis=1)
  
#sort Numpy array by first column
def sort_by_column(data):
    #sortedArr = data[data[:,0].argsort()]
    sortedArr = np.sort(data, axis=0) 
    return sortedArr
  
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        elif (fullPath.endswith('.csv')):
            allFiles.append(fullPath)
                
    return allFiles

dataRoot = '../Create/newAngleOutput_Features/'
output_folder='fps_10_newAngle/'

    
if not os.path.exists(output_folder+'full'):
    os.makedirs(output_folder+'full')
if not os.path.exists(output_folder+'half'):
    os.makedirs(output_folder+'half')

inputData = getListOfFiles(dataRoot)
outputDataFiles = getListOfFiles(output_folder)
    
for file in outputDataFiles:
    os.remove(file)

fps_target=10

report=[]

for file in inputData:
    error=False
    fileName=os.path.basename(file)
    path_data=os.path.split(file)[0]
    folderName=os.path.split(path_data)[1]
    path_data=os.path.split(path_data)[0]
    typeTest=os.path.split(path_data)[1]
    
    file_report=[]
    
    file_report=typeTest+' '+fileName+': '
    
    print("------------------------------------------------")
    print("New File found: ",fileName)
    print("Test Number ",folderName)
    print("Type ",typeTest)


    if(3<=(np.genfromtxt(file, delimiter=',',usecols = range(0,3),dtype ='unicode').shape[0])):
        config = np.genfromtxt(file, delimiter=',',usecols = range(0,3), max_rows =1,dtype ='unicode')
        header = np.genfromtxt(file, delimiter=',', skip_header=1, max_rows =1,dtype ='unicode')
        data = np.genfromtxt(file, delimiter=',', skip_header=2, dtype ='unicode')
        
        #Testing with pandas and comparing reads:
        p_config = pd.read_csv(file, delimiter=',',usecols=range(0,3), nrows =1)
        p_header = pd.read_csv(file, delimiter=',', skiprows=1, nrows=1)
        p_data = pd.read_csv(file, delimiter=',', skiprows=1)
        p_undup = p_data.duplicated(keep='first')

        dups_shape = p_data.pivot_table(index=['frame'], aggfunc='size')
        
        header=np.insert(header,1,0,axis=0)
        header=np.insert(header,1,0,axis=0)
        n_rows, n_columns = data.shape
   
        print("File FPS: ",config[2])
        
    
        #duplicated framename and trial
        base_data = dup_cols(data, 0)
        
        base_data = dup_cols(base_data, 0)
        
        #strip first collumn to have just the frame number
        get_frame_number(base_data, n_rows)

        sorted_pose_data=base_data
        x,y=sorted_pose_data.shape
    
        fps_divider=int(config[2])/fps_target
    
        counter=0
        target_counter=0
        frame_counter=0
        start_frame=0
        sum=[]
        sum_counter=[]
    
        new_pos_data=[[]]
        check_data= [[]]
        
        print("Total frames: ", int(sorted_pose_data[n_rows-1][0]))

        expectedFrames=(int(sorted_pose_data[-1][0])%fps_divider)+(int(sorted_pose_data[-1][0])/int(fps_divider))
        
        print("Expected new frames: ", expectedFrames)
        print("Video duration: ",int(sorted_pose_data[n_rows-1][0])/int(config[2]),"s")
    
        while True:
            if (0==(frame_counter%fps_divider)):
                sum=np.zeros(len(sorted_pose_data[counter]))
                sum_counter=np.zeros(len(sorted_pose_data[counter]))
                start_frame=frame_counter
                check_data.append(sorted_pose_data[counter])
        
            if (int(sorted_pose_data[counter][0])==frame_counter):
           
                row=sorted_pose_data[counter]
                
                for i in range(3,len(row)):
                    if (float(sorted_pose_data[counter][i])!=-1):
                        sum[i]+=float(sorted_pose_data[counter][i])
                        sum_counter[i]+=1
                counter+=1
        
            if (counter!=0):
                if (sorted_pose_data[counter][0]==sorted_pose_data[counter-1][0]):
                    print ("**Duplicated frame corrupted data** "+sorted_pose_data[counter][0])
                    if (error==False):
                        file_report=file_report+'**Duplicated frame corrupted data**'
                        error=True
                    counter+=1
                    frame_counter-=1
                    
                    

            
            frame_counter+=1
        
            if (0==(frame_counter%fps_divider)):
                for i in range(3,len(sum_counter)):
                    if(sum_counter[i]!=0):
                        sum[i]=sum[i]/sum_counter[i]
                  
                    else:
                        sum[i]=-1
                sum[0]=int(start_frame)
                sum[1]=int(frame_counter)-1
                
                new_raw=[]
                
                new_raw.append(sum[0])
                new_raw.append(sum[1])
                new_raw.append(fileName)
                
                for i in range(3,len(sum)):
                    new_raw.append(sum[i])
                
                #new_raw.np.concatenate(sum[0],sum[1],fileName,sum[3:])
                #new_raw.append(sum)

                new_pos_data.append(new_raw)
                target_counter+=1
            
            if (counter>=x-1):
                print("The length of data ", x, " lenght of new data ",len(new_pos_data)," position counter ", counter," New num frames ", target_counter)
                    
                config[2]=10
                header[0]='start_frame'
                header[1]='end_frame'
                header[2]='file_name'
                
                output_path=output_folder+typeTest+'/'+folderName
                
                if (target_counter!=int(sorted_pose_data[n_rows-1][0])/fps_divider):
                    error=True
                    print ('***********Expected frames: ',expectedFrames,' created frames: ',target_counter)
                    file_report=file_report+'** Number of frames created does not match expected**'
                
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                
                print("CSV file is going to be saved in ",output_path)
                
                with open(join(output_path, fileName), mode='w') as p1file:
                    p1writer = csv.writer(p1file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    p1writer.writerow(config)
                    new_pos_data.pop(0)
                    
                    print("New Video duration: ",target_counter/10,"s")
                    
                    p1writer.writerow(header)
                    p1writer.writerows(new_pos_data)
                    print("------------------------------------------------")
                    report.append(file_report)
                break
    else:
        file_report=file_report+'** The file was empty, we are not saving any data'
        report.append(file_report)
        print("The file was empty, we are not saving any data")
        print("------------------------------------------------")

print("------------------------------------------------")
for report_line in report:
    print (report_line)
print("Convertion done!!!!")
print("------------------------------------------------")