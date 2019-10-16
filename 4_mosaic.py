import os
import sys
import datetime
import imageio
from PIL import Image, ImageDraw
import matplotlib
import cv2
import numpy as np
from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
from os.path import isfile, join
from IPython.display import HTML
import io
import base64
import csv
from getpass import getpass
import shutil
import random
import subprocess
import re

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
        elif (fullPath.endswith('.avi')):
            allFiles.append(fullPath)
                
    return allFiles

def frames_to_vid(pathOut,video_name,images,fps):
    pathOut = pathOut+video_name
    frame_array = []
    size=[]
    
    for i in range(len(images)):
        img =  images[i]
        
        height, width, layers = img.shape
        size = (width,height)
        #inserting the frames into an image array
        frame_array.append(img)
    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()

def manual_escape(instr):
    return re.escape(instr)
    
    
    
print('=================================================================')
    
dataRoot = './pointOutput_30_10/'
#folder_videos=os.path.expanduser('~/Tama_Pose_Videos/clips')
#folder_videos=os.path.expanduser('D:\clips/scaled')
folder_videos=os.path.expanduser("./tpd/clips/scaled")
#folder_clip=os.path.expanduser('~/Tama_Pose_Videos/cluster_mosaics/')
#folder_clip=os.path.expanduser('D:\cluster_mosaics/')
folder_clip=os.path.expanduser("./tpd/cluster_points/")

if not os.path.exists(folder_clip):
    os.makedirs(folder_clip)

files_movies=getListOfFiles(folder_videos)


files_inputData = [f for f in os.listdir(dataRoot) if isfile(join(dataRoot, f))]


for csv_file in files_inputData:
    if(csv_file != 'front_hdbscan_25.csv'):
        continue
    if (os.path.splitext(csv_file)[1]!='.csv'): 
        continue
        
    
    fileName=os.path.basename(csv_file)
    
    print ('Cluster File found '+fileName)
    
    if not os.path.exists(folder_clip+fileName.split(".")[0]):
        try:
            os.mkdir(folder_clip+fileName.split(".")[0])
        except OSError:
            print ("Creation of the directory %s failed " % (folder_clip+fileName.split(".")[0]))
        else:
            print ("Successfully created the directory %s " % (folder_clip+fileName.split(".")[0]))
    
    with open(dataRoot+csv_file) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        line_count_f= 0
        
        data=[]
        for row in csv_reader:
            if (line_count_f>1):
                data.append(row)
            line_count_f += 1
        print('Processed ',line_count_f,' lines.')
    
    #count how many cluster in the file
    clust=[]
    n_clust=[]
    for gesture in data:
        clust.append(gesture[5])
        thing_index = n_clust.index(gesture[5]) if gesture[5] in n_clust else -1
        if(thing_index==-1):
            n_clust.append(gesture[5])
    print('The number of clusters found is: ',len(n_clust))
    
    #put same cluster in same data_array, randomize and create video
    
    
    for clust_current in n_clust:
        cluster=[]
        for gesture in data:
            if(gesture[5]==clust_current):
                cluster.append(gesture)
                print("appending", gesture)
        print('We have ',len(cluster),' number of gesture in cluster ',clust_current)
        
        
        for i_video in range(0,5):
            #get 9 random videos
            file_gesture_list=[]
            file_name_gesture_list=[]
            i=0
            watchdog_count =0;
            while(True):
                if(watchdog_count>len(cluster)-1):
                    i_video = 99
                    break
                #if (len(cluster)<9):
                    #i_video=4
                x=random.randint(0, len(cluster)-1)
                print('The RANDOM NUMBER  is: ',x)
                #get video clip file name
                
                tama_type=''
                print('Tama type: ',cluster[x][4])
                print('Full Cluster:', cluster[x])
                if ('half' in cluster[x][4]): 
                    tama_type='half' 
                    print('Tama type will be HALF ')
                else: 
                    tama_type='full'
                    print('Tama type will be FULL ')

                trial_number=cluster[x][3].split('P')[0]
                folder_check=folder_videos+'/'+tama_type+'/Trial_'+str(trial_number).zfill(2)+'/'

                start_f=float(cluster[x][1])
                end_f=float(cluster[x][2])

                file_check=tama_type+'_'+str(trial_number).zfill(2)+'_'+str(int(start_f))+'_'+str(int(end_f))+'.avi'
                
                ft = os.path.join(folder_check,file_check)

                if os.path.isfile(ft):
                    print('Clip file found: '+ft)
                    file_name_gesture_list.append(ft)
                    file_gesture_list.append(cluster[x])
                else:
                    print('****Clip DOES NOT EXIST: '+ft)
                    watchdog_count +=1
                    continue 
                i+=1
                if(i==9):
                    break

            print(file_name_gesture_list)
            
                        
            command_line=[]
            #command_line.append(os.path.expanduser('~/ffmpeg-20190729-43891ea-win64-static/bin/ffmpeg'))
            command_line.append(os.path.expanduser('ffmpeg'))

            for file_name_out in file_name_gesture_list:
                command_line.append('-i')
                command_line.append(file_name_out)

            command_line.append('-filter_complex')
            command_line.append('[0:v][1:v][2:v][3:v][4:v][5:v][6:v][7:v][8:v]xstack=inputs=9:layout=w3_0|w3_h0+h2|w3_h0|0_h4|0_0|w3+w1_0|0_h1+h2|w3+w1_h0|w3+w1_h1+h2[v]')
            command_line.append('-map') 
            command_line.append('[v]')
            command_line.append('-shortest')
            if (str(clust)=='-1'):
                clust='minusone'
            command_line.append(''+folder_clip+fileName.split(".")[0]+'/'+str(clust_current)+'/'+str(clust_current)+'_'+str(i_video)+'.mp4')

            if not os.path.exists(folder_clip+fileName.split(".")[0]+'/'+str(clust_current)):
                os.makedirs(folder_clip+fileName.split(".")[0]+'/'+str(clust_current))
            
            if os.path.isfile(folder_clip+fileName.split(".")[0]+'/'+str(clust_current)+'/'+str(clust_current)+'_'+str(i_video)+'.mp4'):
                print('**************Video does exist, skipping')
                continue
            else:
                subprocess.call(command_line)

            print('-----------------------------------------------------------------')
    print('=================================================================')
print('Done!')
print('=================================================================')




#ffmpeg -i 474_9480_9541.avi -i 380_7600_7661.avi -i 287_5740_5801.avi -i 193_3860_3921.avi  -filter_complex "[0:v][1:v]hstack[t];[2:v][3:v]hstack[b];[t][b]vstack[v]" -map "[v]" -shortest output.mp4
        
        
        