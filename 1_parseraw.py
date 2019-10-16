import os
from os import listdir
from os.path import isfile, join
from math import hypot, atan2, degrees 
import json
import csv
import tarfile
import sys
import math

outputType = "Features" #PointsProb = points and probability score, Points = just points, Features = computed features

pi = 3 #index to identify people 3=x of spinetop

def distance(pointA, pointB):
  "returns -1 if either point doesn't exist"
  if (pointA[0]==0 and pointA[1]==0) or (pointB[0]==0 and pointB[1]== 0):
    return -1

  return hypot(pointA[0]-pointB[0], pointA[1]-pointB[1])


def angle(pointA, pointB):
  "returns -1 if either point doesn't exist"
  if (pointA[0]==0 and pointA[1]==0) or (pointB[0]==0 and pointB[1]== 0):
    return -1

  return degrees(atan2(pointA[0]-pointB[0], pointA[1]-pointB[1]))


def ratio(lenA, lenB):
  "returns -1 if either point doesn't exist or has length 0"
  if lenA<=0 or lenB<=0:
    return -1

  return lenA/lenB


def findClosest(v, hay):
  dist = sys.maxsize
  i = -1;
  for key in range(0, len(hay)):
    test = abs(hay[key]-v)
    if(test<dist):
      i=key
      dist=test
  
  return i


def processFolder(inputs, outputs, header_list):
    tl=0


    rootPath = outputs
    folderPath = inputs

    #tar = tarfile.open(tarPath)
    #filelistunsorted = tar.getmembers()

    filelistunsorted = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]

    filelist = sorted(filelistunsorted)

    print(len(filelist))

    #print(filelist)

    #filelist = [f for f in listdir(rootPath) if isfile(join(rootPath, f))]

    #Data indexes: 
    #(3,4,5) = SpineTop
    #(6,7,8) & (15,16,17) = shoulders
    #(0,1,2) = nose
    #(51,52,53) & (54,55,56) = ears
    #(45,46,47) & (48,49,50) = eyes

    #Ouput Holder
    #header = ['frame', 'shoulder_angle', 'shoulder_distance', 'shoulder_ratio', 'right_ear_angle', 'right_ear_distance', 'left_ear_angle', 'left_ear_distance', 'right_nose_eye_angle', 'right_nose_eye_distance', 'left_nose_eye_angle','left_nose_eye_distance', 'nose_angle', 'nose_distance', 'eyes_angle', 'eyes_distance']


    if outputType == "PointsProb": 
        header = ['frame', 'spinex', 'spiney', 'spinep', 'lsx', 'lsy', 'lsp', 'rsx', 'rsy', 'rsp', 'nx','ny', 'np', 'rex', 'rey', 'rep', 'lex', 'ley', 'lep', 'ryy', 'ryx', 'ryp','lyx', 'lyy', 'lyp']
    elif outputType == "Points":
        header = ['frame', 'spinex', 'spiney', 'lsx', 'lsy', 'rsx', 'rsy', 'nx','ny', 'rex', 'rey', 'lex', 'ley', 'ryy', 'ryx','lyx', 'lyy']
    else:
        header = ['frame', 'shoulder_angle', 'shoulder_distance', 'shoulder_ratio', 'right_ear_angle', 'right_ear_distance', 'left_ear_angle', 'left_ear_distance', 'right_nose_eye_angle', 'right_nose_eye_distance', 'left_nose_eye_angle','left_nose_eye_distance', 'nose_angle', 'nose_distance', 'eyes_angle', 'eyes_distance']
        

    csvData = [[],[],[],[]]

    countEarly = 0;
    ct = 0
    count = 0
    c1=0
    c2=0
    c3=0
    c4=0
    count5= 0
    print("Should loop for ", len(filelist))

    personIndexes = [];
    personIndexes2 = [];    
    personWidths = [];
    

    for jf in filelist:
      countEarly = countEarly + 1
      if jf.endswith(".json"):
        #with tar.extractfile(jf) as jsonFile:
        #print (join(folderPath, jf))

        #Extra loop to calculate max shoulder width
        with open(join(folderPath, jf)) as jsonFile:
            ct=ct+1
            try:
                frameData = json.load(jsonFile)
            except: 
                continue
      
            #print(frameData)
            if len(frameData['people']) > 4: 
              count5 = count5+1
              continue

            if len(frameData['people']) == 1:
              c1 = c1 + 1
            if len(frameData['people']) == 2:
              c2 = c2 + 1
            if len(frameData['people']) == 3:
              c3 = c3 + 1
              continue
            if len(frameData['people']) == 4:
              c4 = c4 + 1
   

            count = count + 1
            sortedFrame = dict(frameData) 
            sortedFrame['people'] = sorted(frameData['people'], key=lambda x : x['pose_keypoints_2d'][pi], reverse=False)

            #set the initial person indexes, or remake them if there is a new person found
            if(len(personIndexes2) < len(frameData['people'])):
              print ("Adding people Widths", jf)
              pisx = 0
              for person in sortedFrame['people']:
                if(pisx==len(personIndexes2)):
                  personIndexes2.insert(len(personIndexes2),person['pose_keypoints_2d'][pi])
                  personWidths.insert(len(personIndexes2),0)
                else:
                  personIndexes2[pisx] = person['pose_keypoints_2d'][pi];
                pisx = pisx + 1
              print("People Points Widths: ", personIndexes2)

            for person in sortedFrame['people']:
              p25 = person['pose_keypoints_2d']
              dataIndex = findClosest(p25[pi], personIndexes2)
              dist = distance([p25[6], p25[7]], [p25[15], p25[16]])
              if(personWidths[dataIndex] < dist):
                  personWidths[dataIndex] = dist
                  #print("People Widths: ", personWidths)
                  
        
        
        
        with open(join(folderPath, jf)) as jsonFile:

          ct=ct+1
          try:
              frameData = json.load(jsonFile)
          except: 
              continue
      
          #print(frameData)
          if len(frameData['people']) > 4: 
            count5 = count5+1
            continue

          if len(frameData['people']) == 1:
            c1 = c1 + 1
          if len(frameData['people']) == 2:
            c2 = c2 + 1
          if len(frameData['people']) == 3:
            c3 = c3 + 1
            continue
          if len(frameData['people']) == 4:
            c4 = c4 + 1
   

          count = count + 1
          sortedFrame = dict(frameData) 
          sortedFrame['people'] = sorted(frameData['people'], key=lambda x : x['pose_keypoints_2d'][pi], reverse=False)

          #set the initial person indexes, or remake them if there is a new person found
          if(len(personIndexes) < len(frameData['people'])):
            print ("Adding people", jf)
            pisx = 0
            for person in sortedFrame['people']:
              if(pisx==len(personIndexes)):
                personIndexes.insert(len(personIndexes),person['pose_keypoints_2d'][pi])
              else:
                personIndexes[pisx] = person['pose_keypoints_2d'][pi];
              pisx = pisx + 1
            print("People Points: ", personIndexes)



          di_check = [0,0,0,0]
          for person in sortedFrame['people']:
            p25 = person['pose_keypoints_2d']
            #print(person['pose_keypoints_2d'][0])
        
            #Data indexes: 
            #(3,4,5) = SpineTop
            #(6,7,8) & (15,16,17) = shoulders
            #(0,1,2) = nose
            #(51,52,53) & (54,55,56) = ears
            #(45,46,47) & (48,49,50) = eyes

    
            dataIndex = findClosest(p25[pi], personIndexes)
            if(di_check[dataIndex]>0):
                continue
            else:
                di_check[dataIndex] += 1
                
            if outputType == "PointsProb": 
                #header = ['frame', 'spinex', 'spiney', 'spinep', 'lsx', 'lsy', 'lsp', 'rsx', 'rsy', 'rsp', 'nx','ny', 'np', 'rex', 'rey', 'rep', 'lex', 'ley', 'lep', 'ryy', 'ryx', 'ryp','lyx', 'lyy', 'lyp']
                csvData[dataIndex].append([jf, p25[3], p25[4], p25[5], p25[6], p25[7], p25[8], p25[15], p25[16], p25[17], p25[0], p25[1], p25[2], p25[51], p25[52], p25[53], p25[54], p25[55], p25[56], p25[45], p25[46], p25[47], p25[48], p25[49], p25[50]])
            elif outputType == "Points":
                #header = ['frame', 'spinex', 'spiney', 'lsx', 'lsy', 'rsx', 'rsy', 'nx','ny', 'rex', 'rey', 'lex', 'ley', 'ryy', 'ryx','lyx', 'lyy']
                csvData[dataIndex].append([jf, p25[3], p25[4], p25[6], p25[7], p25[15], p25[16], p25[0], p25[1], p25[51], p25[52], p25[54], p25[55], p25[45], p25[46], p25[48], p25[49]])
            else:
                #shoulders
                shoulder_length = distance([p25[6], p25[7]], [p25[15], p25[16]])
                #shoulder_angle = angle([p25[6], p25[7]], [p25[15], p25[16]])
                s_a_length = distance([p25[6], p25[7]], [p25[3], p25[4]])
                s_b_length = distance([p25[3], p25[4]], [p25[15], p25[16]])
                shoulder_ratio = ratio(s_a_length, s_b_length)
                
                #New shoulder calculation
                #Logic: Find max shoulder width
                #left shoulder is at x,y,o
                #right shoulder is max_width_2 =  (x1 - x2)_2 + (y1-y2)_2 + (0 - z2)_2
                # so z = width_2 - ((x1-x2)_2 + (y1-y2)_2)
                #then if x2>x1 the angle is = tan-1 (Z2 / x2-x1)
                #or if x2<x1 the angle is 180- tan-1 (Z2 / x2-x1)
                #Check left or right. So if L is lower than R
                

                
                if(p25[6] < p25[15]):
                    x1 = float(p25[6]) #LX
                    y1 = float(p25[7]) #LY
                    x2 = float(p25[15]) #RX
                    y2 = float(p25[16]) #RY
                    z1 = float(0)
                else:
                    x2 = float(p25[6]) #RX
                    y2 = float(p25[7]) #RY
                    x1 = float(p25[15]) #LX
                    y1 = float(p25[16]) #LY
                    z1 = float(0)
                
                try:
                    shoulder_z = math.sqrt(abs(math.pow(personWidths[dataIndex], 2) - math.pow((x1-x2), 2) - math.pow((y1-y2), 2)))
                    shoulder_angle = 90
                except ValueError:
                    print("Z Calc", personWidths[dataIndex], x1, x2, y1, y2)
                
                try:                
                    if x2>x1:
                        shoulder_angle = math.degrees(math.atan(shoulder_z /(x2-x1)))    
                    else:
                        shoulder_angle = 180 - math.degrees(math.atan(shoulder_z /(x2-x1)))    
                except:
                    print("EQUALS Z Calc", personWidths[dataIndex], x1, x2, y1, y2)
                    print("EQUALSAngle Calc", shoulder_z,x2,x1, " = ", shoulder_angle)
                    
                if shoulder_angle > 180:
                    print("180 + Z Calc", personWidths[dataIndex], x1, x2, y1, y2)
                    print("180 + Angle Calc", shoulder_z,x2,x1, " = ", shoulder_angle)
                
                shoulder_angle = round(shoulder_angle, 6)

                #ear-eye
                right_ear_eye_angle = angle([p25[51], p25[52]], [p25[45], p25[46]])
                left_ear_eye_angle = angle([p25[54], p25[55]], [p25[48], p25[49]])
                right_ear_eye_distance = distance([p25[51], p25[52]], [p25[45], p25[46]])
                left_ear_eye_distance = distance([p25[54], p25[55]], [p25[48], p25[49]])

                #eye-nose
                right_nose_eye_angle = angle([p25[51], p25[52]], [p25[0], p25[1]])
                left_nose_eye_angle = angle([p25[54], p25[55]], [p25[0], p25[1]])
                right_nose_eye_distance = distance([p25[51], p25[52]], [p25[0], p25[1]])
                left_nose_eye_distance = distance([p25[54], p25[55]], [p25[0], p25[1]])

                #nose-neck
                nose_neck_distance = distance([p25[0], p25[1]], [p25[3], p25[4]])
                nose_neck_angle = angle([p25[0], p25[1]], [p25[3], p25[4]])

                #eye-eye
                eye_distance = distance([p25[51], p25[52]], [p25[54], p25[55]])
                eye_angle = angle([p25[51], p25[52]], [p25[54], p25[55]])
                
                csvData[dataIndex].append([jf, shoulder_angle, shoulder_length, shoulder_ratio, right_ear_eye_angle, right_ear_eye_distance, left_ear_eye_angle, left_ear_eye_distance, right_nose_eye_angle, right_nose_eye_distance, left_nose_eye_angle, left_nose_eye_distance, nose_neck_angle, nose_neck_distance, eye_angle, eye_distance])    
        
      else:
        print("Skipping file ", jf)


    #Write out 4 csv files, one for each person

    print("1 ", len(csvData[0]), " 2 ", len(csvData[1]), " 3 ", len(csvData[2]), " 4 ", len(csvData[3]))
    
    print(rootPath)
    
    #some sort of reduce to frameRate
    
    #csvData[0] = P1, [1] = P2 etc.
    
    #
    

    outName = header_list[3]+"P1_"+header_list[0]+".csv"
    with open(join(rootPath, outName), mode='w') as p1file:
      p1writer = csv.writer(p1file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      p1writer.writerow(['L', header_list[0], header_list[2]])
      p1writer.writerow(header)
      p1writer.writerows(csvData[0])

    outName = header_list[3]+"P2_"+header_list[0]+".csv"
    with open(join(rootPath, outName), mode='w') as p1file:
      p1writer = csv.writer(p1file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      p1writer.writerow(['R', header_list[0], header_list[2]])
      p1writer.writerow(header)
      p1writer.writerows(csvData[1])  

    outName = header_list[3]+"P1_"+header_list[1]+".csv"
    with open(join(rootPath, outName), mode='w') as p1file:
      p1writer = csv.writer(p1file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      p1writer.writerow(['L', header_list[1], header_list[2]])              
      p1writer.writerow(header)
      p1writer.writerows(csvData[2])  

    outName = header_list[3]+"P2_"+header_list[1]+".csv"
    with open(join(rootPath, outName), mode='w') as p1file:
      p1writer = csv.writer(p1file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      p1writer.writerow(['R', header_list[1], header_list[2]])              
      p1writer.writerow(header)
      p1writer.writerows(csvData[3])


    print ("Good ", count, " All ", countEarly)
    print ("1p ", c1, " 2p ", c2, " 3p ", c3, " 4p ", c4, " >4p ", count5)
    tl = tl + 1


input_list=[
    "./rawData/full/Trial 1/",
    "./rawData/full/Trial 2/",
    "./rawData/full/Trial 4/",
    "./rawData/full/Trial 5/",
    "./rawData/full/Trial 6/",
    "./rawData/full/Trial 7/",
    "./rawData/full/Trial 8/",    
    "./rawData/full/Trial 9/",
    "./rawData/full/Trial 10/",
    "./rawData/full/Trial 11/",
    "./rawData/half/Trial 1/",
    "./rawData/half/Trial 2/",
    "./rawData/half/Trial 4/",
    "./rawData/half/Trial 5/",
    "./rawData/half/Trial 6/",
    "./rawData/half/Trial 7/",
    "./rawData/half/Trial 8/",
    "./rawData/half/Trial 10/",
    "./rawData/half/Trial 11/"]

output_list=[
    "/full/Trial 1/",
    "/full/Trial 2/",
    "/full/Trial 4/",
    "/full/Trial 5/",
    "/full/Trial 6/",
    "/full/Trial 7/",
    "/full/Trial 8/",    
    "/full/Trial 9/",
    "/full/Trial 10/",
    "/full/Trial 11/",
    "/half/Trial 1/",
    "/half/Trial 2/",
    "/half/Trial 4/",
    "/half/Trial 5/",
    "/half/Trial 6/",
    "/half/Trial 7/",
    "/half/Trial 8/",
    "/half/Trial 10/",
    "/half/Trial 11/"]
    
header_list=[
    ["B","X","100", "1"],
    ["B","F","24", "2"],
    ["B","F","30", "4"],
    ["F","B","60", "5"],
    ["B","F","60", "6"],
    ["F","B","60", "7"],
    ["B","F","60", "8"],    
    ["B","F","60", "9"],
    ["B","F","60", "10"],
    ["F","B","30", "11"],
    ["B","X","100", "1"],
    ["B","F","24", "2"],
    ["B","F","30", "4"],
    ["F","B","60", "5"],
    ["B","F","60", "6"],
    ["F","B","60", "7"],
    ["B","F","60", "8"],
    ["B","F","60", "10"],
    ["F","B","30", "11"]]

outputPrefix = "./rawTESTOutput_"+outputType


fi=-1
for inputFolder in input_list:
    
    fi = fi + 1
    if not os.path.exists(inputFolder):
        continue 
        
    if not os.path.exists(outputPrefix+output_list[fi]):
        os.makedirs(outputPrefix+output_list[fi])
    
    processFolder(inputFolder, outputPrefix+output_list[fi], header_list[fi])
    
    
    
    
    
    

