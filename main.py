import os
import pickle
import face_recognition
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, storage
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://faceattendancerealtime-167bf-default-rtdb.firebaseio.com/",
    'storageBucket' : "faceattendancerealtime-167bf.appspot.com"
})
bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

#Importing the mode images into a list
folderModePath = 'Resources/Modes' #just ot tackle the different folder structure
modePathList = os.listdir(folderModePath)  #this will get the names of all the images in the folder
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

#Load the Encoding file
print("Loading Encode File....")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0), None, 0.25, 0.25)  #smallig the image to reduce the computation power
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #we need two things,
    # 1- > faces in the current frame
    # 2 -> its encoding
    faceCurFrame = face_recognition.face_locations(imgS)
    #we dont want to find the location of the whole image, we are just extracting thr faces
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # imgBackground[167:167+480, 57:57+640] = img
    #row , col
    imgBackground[180:180 + 480, 82:82 + 640] = img
    imgBackground[48:48 + 619, 811:811 + 405] = imgModeList[modeType]

    if  faceCurFrame:

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            #lower the distance then its a better match
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]  :
                # print("known face detected")
                # print(studentIds[matchIndex])
                id = studentIds[matchIndex]
                if counter == 0:
                    cv2.putText(imgBackground, "Loading", (400,400), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                #get the data from database
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                #get the image from storage database
                blob = bucket.get_blob(f'Images/{id}.png')
                array =   np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                #updating data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_Attendance_Time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                # print(secondsElapsed)
                if secondsElapsed > 30: #time should be in hour in realtime -> time neds to be in converted in seconds
                    #suppose 12 hrs minimum elapsed time then 12hrs should be converted to seconds
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_Attendance_Time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[48:48 + 619, 811:811 + 405] = imgModeList[modeType]

            if modeType != 3: #if not already marked
                if 10 < counter < 20:   #show marked
                    modeType = 2
                imgBackground[48:48 + 619, 811:811 + 405] = imgModeList[modeType]

                if counter <= 10 : #show the student info in the mod

                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (900, 100),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(imgBackground, str(id), (970, 485),
                                cv2.FONT_HERSHEY_COMPLEX, 0.9, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Major']), (940, 542),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Standing']), (875, 609),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,0), 2)
                    cv2.putText(imgBackground, str(studentInfo['Year']), (975, 609),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,0,0), 2)
                    cv2.putText(imgBackground, str(studentInfo['Starting Year']), (1100, 609),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7,(0,0,0), 2)

                    (width, height), _ =cv2.getTextSize(studentInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (405-width)//2
                    cv2.putText(imgBackground, str(studentInfo['Name']), (820+offset, 436),
                                 cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

                    imgStudentResized = cv2.resize(imgStudent, (220, 217))  # Note the order of dimensions
                    imgBackground[177:177 + 217, 904:904 + 220] = imgStudentResized


            if counter >= 20:
                modeType = 0
                studentInfo = []
                imgStudentResized = []
                imgBackground[48:48 + 619, 811:811 + 405] = imgModeList[modeType]
                counter = 0
            counter += 1
        print(counter)
    else:
        print("No Face Detction -0 ")
        modeType = 0
        counter = 0


    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)