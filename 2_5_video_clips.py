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
        elif (fullPath.endswith('.mp4')):
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
    
    
    
dataRoot = 'manual/'
folder_videos=os.path.expanduser('~/Dropbox/Tama Video Data/OpenPose Data/Tama_Pose_Videos/')
folder_clip=os.path.expanduser('~/Dropbox/Tama Video Data/OpenPose Data/Tama_Pose_Videos/clips/')

if not os.path.exists(folder_clip):
    os.makedirs(folder_clip)

files_movies=getListOfFiles(folder_videos+'/half_Tama/')
files_movies=files_movies+getListOfFiles(folder_videos+'/full_Tama/')

files_inputData = [f for f in os.listdir(dataRoot) if isfile(join(dataRoot, f))]
tests = []

print("Video tests found in this directory:")
for i in range(len(files_movies)):

    fileName=os.path.basename(files_movies[i])
    path_data=os.path.split(files_movies[i])[0]
    typeTest=os.path.split(path_data)[1].split("_")[0]
    
    tests.append(fileName.split(".")[0])
    
    if not os.path.exists(folder_clip+typeTest+'/'):
        os.makedirs(folder_clip+typeTest+'/')
    
    new_folder=folder_clip+typeTest+'/'+tests[i].split("_")[1]+'_'+tests[i].split("_")[2]
    
    if not os.path.exists(new_folder):
        try:
            os.mkdir(new_folder)
        except OSError:
            print ("Creation of the directory %s failed " % (new_folder))
        else:
            print ("Successfully created the directory %s " % (new_folder))


for i in range(len(files_movies)):
    first_frame_f = []
    last_frame_f = []
    first_frame_b = []
    last_frame_b = []
    
    fileName=os.path.basename(files_movies[i])
    path_data=os.path.split(files_movies[i])[0]
    typeTest=os.path.split(path_data)[1].split("_")[0]
    trialNumber=int(fileName.split(".")[0].split("_")[2])
        
    count = 0
    csv_file_f=dataRoot+typeTest+'_Trial '+str(trialNumber)+'_'+str(trialNumber)+'P1_f.csv'
    csv_file_b=dataRoot+typeTest+'_Trial '+str(trialNumber)+'_'+str(trialNumber)+'P1_b.csv'
    
    csv_found=[False,False]
    
    if os.path.isfile(csv_file_f):
        print ('CSV FILE EXISTS '+csv_file_f)
        with open(csv_file_f) as csvfile:
            csv_reader_f = csv.reader(csvfile, delimiter=',')
            csv_found[0]=True
            line_count_f= 0
            for row in csv_reader_f:
                if (line_count_f!=0):
                    first_frame_f.append(row[1])
                    last_frame_f.append(row[2])
                line_count_f += 1
            print('Processed ',line_count_f,' lines.')
    else:
        print ('NOOOOOOOOO! CSV FILE DOESNT EXIST!!! '+csv_file_f)
    
    if os.path.isfile(csv_file_b):
        print ('CSV FILE EXISTS '+csv_file_b)
        with open(csv_file_b) as csvfile:
            csv_reader_b = csv.reader(csvfile, delimiter=',')
            csv_found[1]=True
            line_count_b = 0
            for row in csv_reader_b:
                if (line_count_b!=0):
                    first_frame_b.append(row[1])
                    last_frame_b.append(row[2])
                line_count_b += 1
            print('Processed ',line_count_b,' lines.')
    else:
        print ('NOOOOOOOOO! CSV FILE DONT EXISTS!!! '+csv_file_b)
    
    if ((csv_found[0]==True) and (csv_found[1]==True)):
        if (line_count_f<line_count_b):
            first_frame_f=first_frame_b
            last_frame_f=last_frame_b
    elif ((csv_found[0]==True) and (csv_found[1]==False)):
        first_frame_f=first_frame_f
        last_frame_f=last_frame_f
    elif ((csv_found[0]==False) and (csv_found[1]==True)):
        first_frame_f=first_frame_b
        last_frame_f=last_frame_b
    else:
        continue
        
    #preload video
    #vidcap_preload = cv2.VideoCapture(folder_videos+typeTest+'_Tama/'+os.path.basename(files_movies[i]))
    #fps_preload=vidcap_preload.get(cv2.CAP_PROP_FPS)    # OpenCV2 version 2 used "CV_CAP_PROP_FPS")
    
    class clip_ob(object):
        images_=[]
        first=0
        last=0
        type_test=''
        num_test=''
        path=''
        file=''
        fps=0
        count_push=0
        #constructor
        def __init__(self, first, last,type_test,num_test,path,file,fps):
            self.first = int(first)
            self.last = int(last)
            self.type_test = type_test
            self.num_test = num_test
            self.path=path
            self.file=file
            self.fps=fps
            n_frames=float(last_frame_f[j])-float(first_frame_f[j])
            self.images_= []

        def push_image(self,count,image_):
            if ((count<=int(self.last))and(count>=int(self.first))):
                self.count_push=self.count_push+1
                self.images_.append(image_)
                
        def ready(self):
            clip_length=(int(self.last)-int(self.first))
            if (len(self.images_)>=clip_length):
                return(True)
            else:
                return(False)
        def length(self):
            return(len(self.images_))
        def save(self):
            frames_to_vid(self.path,self.file,self.images_,self.fps)
            print(self.file+' SAVED AS CLLIP')
        def getType(self):
            return(self.type_test)
        def getNum(self):
            return(self.num_test)
        def getFile(self):
            return(self.file)
    
    
    vidcap = cv2.VideoCapture(folder_videos+typeTest+'_Tama/'+os.path.basename(files_movies[i]))
    fps=vidcap.get(cv2.CAP_PROP_FPS)    # OpenCV2 version 2 used "CV_CAP_PROP_FPS")
    
    
    aux=[]
    
    print('----------------------------------------------------------------------------------')
    
    for j in range(len(first_frame_f)):
        
        firstFrame_str=str(first_frame_f[j]).split(".")[0]
        lastFrame_str=str(last_frame_f[j]).split(".")[0]
        new_clip_folder=folder_clip+typeTest+'/'+tests[i].split("_")[1]+'_'+tests[i].split("_")[2]+'/'
        new_clip_file=typeTest+'_'+tests[i].split("_")[2]+'_'+firstFrame_str+'_'+lastFrame_str+'.avi'
        firstFrame=float(first_frame_f[j])
        lastFrame=float(last_frame_f[j])
        
        if os.path.isfile(new_clip_folder+new_clip_file):
            print('File already exists:',new_clip_file)
        else:
            aux.append(clip_ob(firstFrame,lastFrame,typeTest,tests[i].split("_")[2],new_clip_folder,new_clip_file,fps))
    
    print('----------------------------------------------------------------------------------')
    
    count=0
    print(len(aux),' clips will be extracted')
    if (len(aux)>0):
        while True:
            for clip_aux in aux:
                if (clip_aux.ready()):
                    clip_aux.save()
                    aux.remove(clip_aux)
            success,image = vidcap.read()
            if not success:
                print('Video read no success')
                break
            else:
                for j in range(len(aux)):
                    aux[j].push_image(count,image)
            count += 1
    else:
        print('Trial ',tests[i].split("_")[2],' Has all clips done')
    print('==============================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')
print('============================= TITI JA POTS APAGAR ==========================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')
print('===========##############=####====####=##########==========================================')
print('===========##############=####====####=##########===========================================')
print('================####======####====####=####=================================================')
print('================####======############=##########===========================================')
print('================####======############=##########===========================================')
print('================####======####====####=####=================================================')
print('================####======####====####=##########===========================================')
print('================####======####====####=##########===========================================')
print('============================================================================================')
print('============================================================================================')
print('===========##########=####====####=########=================================================')
print('===========##########=#####===####=####==####==============================================')
print('===========####=======######==####=####=====####=============================================')
print('===========##########=#######=####=####======####==========================================')
print('===========##########=############=####======####===========================================')
print('===========####=======####=#######=####=====####============================================')
print('===========##########=####==######=####==####==============================================')
print('===========##########=####====####=########=================================================')
print('============================================================================================')
print('============================================================================================')
print('============================================================================================')


print('Done!')
