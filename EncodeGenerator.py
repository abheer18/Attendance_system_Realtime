import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://faceattendancerealtime-167bf-default-rtdb.firebaseio.com/",
    'storageBucket' : "faceattendancerealtime-167bf.appspot.com"
})
#Importing the STUDENT IMAGES
folderPath = 'Images' #just ot tackle the different folder structure
pathList = os.listdir(folderPath)  #this will get the names of all the images in the folder
imgList = []
studentIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0]) #ex ---> 1002.png
    fileName = f'{folderPath}/{path}' #sending data to database
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

#will create a folder images and put all images in it
#we are going to loop every image and encode it
#Process of encoding
# step1 - change the color space (bgr to rgb)
# step2 - find the encodings
def findEncodings(imageList):
    encodeList = []
    for img in imageList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
print("Encoding Started....")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds] #we need to store these list in a file
print(encodeListKnown)
print("Encoding Complete")
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)   #simply putting the data in the file
file.close()
print("File Saved")
