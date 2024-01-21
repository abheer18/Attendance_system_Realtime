import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://faceattendancerealtime-167bf-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "1001":
        {
            "Name" : "Abheer Raj Mehrotra",
            "Major" : "Machine Learning",
            "Starting Year" : 2020,
            "total_attendance" : 4,
            "Standing" : "G",
            "Year" : "4",
            "last_Attendance_Time" : "2024-01-14 00:54:32"
        },
    "1002":
        {
            "Name" : "Sundar Pichai",
            "Major" : "Semi Conductor",
            "Starting Year" : 2001,
            "total_attendance" : 14,
            "Standing" : "G",
            "Year" : "4",
            "last_Attendance_Time" : "2024-01-24 00:54:32"
        },
    "1003":
        {
            "Name" : "Jeff Bezos",
            "Major" : "Gen AI",
            "Starting Year" : 2002,
            "total_attendance" : 15,
            "Standing" : "G",
            "Year" : "4",
            "last_Attendance_Time" : "2024-01-16 00:54:32"
        }
}

for key, value in data.items():
    ref.child(key).set(value)