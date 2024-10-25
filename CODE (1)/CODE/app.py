import csv
from sklearn.preprocessing import LabelEncoder
from flask import Flask,render_template,request,flash
import cv2,os
import mysql.connector
import pandas as pd
from PIL import Image
import numpy as np
import datetime
import time
import math
import pickle
import requests
import calendar
app=Flask(__name__)
app.config['SECRET_KEY']='attendance system'
mydb = mysql.connector.connect(host="localhost", user="root", passwd="", port=3307, database="smart_attendance")
cursor = mydb.cursor()
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        email = request.form['uname']
        password = request.form['password']
        if (email=='admin') and (password=='admin'):
            flash('Admin login successful','success')
    return render_template('admin.html')
@app.route("/addback", methods=['POST','GET'])
def addback():
    if request.method=='POST':
        Id=request.form['rno']
        name=request.form['name']
        pno=request.form['pno']
        print(type(Id))
        print(type(name))
        print(type(pno))
        if not Id:
           flash("Please enter roll number properly ","warning")
           return render_template('index.html')


        elif not name:
            flash("Please enter your name properly ", "warning")
            return render_template('index.html')
        elif not pno:
            flash("Please enter mobile number","warning")
        # elif (Id.isalpha() and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "Haarcascade/haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0
        df = pd.read_csv("Student_Details/StudentDetails.csv")
        val = df.Id.values
        if Id in str(val):
            flash("Roll already exists", "danger")
            return render_template("index.html")

        else:
            while (True):
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        # incrementing sample number
                    sampleNum = sampleNum + 1
                        # saving the captured face in the dataset folder TrainingImage
                    cv2.imwrite("TrainingImage/ " + name + "." + Id + '.' + str(
                            sampleNum) + ".jpg", gray[y:y + h, x:x + w])
                        # display the frame

                else:
                    cv2.imshow('frame', img)
                    # wait for 100 miliseconds
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                    # break if the sample number is morethan 100
                elif sampleNum > 250:
                        break
        cam.release()
        cv2.destroyAllWindows()
        # res = "Roll Number : " + Id + " Name : " + name
        row = [Id, name, pno]
        with open('Student_Details/StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        flash("Captured images successfully!!","success")
        return render_template("admin.html")
        # else:
        #     if (Id.isalpha()):
        #         flash("Enter Alphabetical Rollnumber", "info")
        #         return render_template("index.html")
        #
        #     if (name.isalpha()):
        #         flash("Enter Alphabetical Name", "danger")
        #         return render_template("index.html")
        # return render_template("index.html")
    return render_template("index.html")
@app.route('/trainback')
def trainback():
    le = LabelEncoder()
    faces, Id = getImagesAndLabels("TrainingImage")
    Id = le.fit_transform(Id)
    output = open('label_encoder.pkl', 'wb')
    pickle.dump(le, output)
    output.close()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(Id))
    recognizer.save(r"Trained_Model\Trainner.yml")

    flash("Model Trained Successfully", "success")
    return render_template('admin.html')

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        Id = str(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids
@app.route('/view_students')
def view_students():
    df=pd.read_csv('Student_Details/StudentDetails.csv')

    return render_template('view_students.html',col_name = df.columns,row_val = list(df.values.tolist()))
@app.route('/admin')
def admin():
   return render_template('admin.html')
def findDay(date):
    day, m1, year = (int(i) for i in date.split('-'))
    dayNumber = calendar.weekday(year, m1, day)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
    return (days[dayNumber])
@app.route('/view_report', methods=['POST'])
def view_report():
    if request.method=="POST":
        opt=request.form['opt']
        rno=request.form['rno']

        if opt=="day":
            sql="select * from attendance where date1='"+rno+"'"
            cursor.execute(sql, mydb)
            data = cursor.fetchall()
            msg='Day Attendance Report'

        else:
            sql = "select * from attendance where m1='" + rno + "'"
            cursor.execute(sql, mydb)
            data = cursor.fetchall()
            msg='Month Attendance Report'
        return render_template('view_report.html',data=data,msg=msg,a=rno)

@app.route('/prediction')
def prediction():
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
    recognizer.read(r"Trained_Model\Trainner.yml")
    harcascadePath = r"Haarcascade\haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);
    # df = pd.read_csv(r"Student_Details\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    # print(df)
    font = cv2.FONT_HERSHEY_SIMPLEX
    pkl_file = open('label_encoder.pkl', 'rb')
    le = pickle.load(pkl_file)
    pkl_file.close()
    data = pd.read_csv("D:\final code\CODE (1)\CODE\Student_Details\StudentDetails.csv")
    # print(data)
    # rollno=data['Id']
    val = str(data.Id.values)

    det=0
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
            # print(conf)
            if (conf < 50):
                det += 1
                tt = le.inverse_transform([Id])
                # print(type(tt))
                tt = tt[0]
                r1=int(tt)
                # print(r1)
                rno=str(tt)
                mobile_number=data[data['Id'] == r1]
                mobile_number=mobile_number['MobileNumber']
                # print('Mobile Number:',mobile_number)
                # # print(rno)
                b=list(mobile_number)
                print(b)
                bb=b[0]
                student_name = data[data['Id'] == r1]
                student_name = student_name['Name']
                # print('Mobile Number:',mobile_number)
                # # print(rno)
                a = list(student_name)
                aa = a[0]
                # aa=a
                print(a)
                # bb=str(b)
                # bb=pd.Series(bb)
                # print(bb.values)
                # print(type(bb))


                if det==50:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    # in_time = int(timeStamp.split(':')[0]) * 60
                    in_time=400
                    # print(in_time)
                    sql = "select count(*) from attendance where rno='%s' and date1='%s'" % (rno, date)
                    z = pd.read_sql_query(sql, mydb)
                    count = z.values[0][0]
                    if 600 >= in_time:# Befor 10
                        print("hhhhhhhhhh")
                        if count == 0:
                            status='Early Coming'
                            sql = "insert into attendance(rno,in_time,in_status,date1) values(%s,%s,%s,%s)"
                            val = (rno, timeStamp, status, date)
                            cursor.execute(sql, val)
                            mydb.commit()
                            url = "https://www.fast2sms.com/dev/bulkV2"

                            message = aa+" attended at on time "+timeStamp +"."
                            no = bb
                            print(no)
                            print(type(no))
                            data1 = {
                                "route": "q",
                                "message": message,
                                "language": "english",
                                "flash": 0,
                                "numbers": no,
                            }

                            headers = {
                                "authorization": "OmnbyZilA0HtvwKekDd8JGpM1VR3XsQcNCBx5TWrUYj297F46Etwu4IYkPTpyEM7DJ8Ve2rqZzNo69hX",
                                "Content-Type": "application/json"
                            }

                            response = requests.post(url, headers=headers, json=data1)
                            print(response)


                        else:
                            s = "Early Out"
                            sq = "update attendance set out_time='%s',out_status='%s' where rno='%s' and date1='%s'" % (
                            timeStamp, s, rno, date)
                            cursor.execute(sq)
                            mydb.commit()
                            url = "https://www.fast2sms.com/dev/bulkV2"

                            message = str(aa) + " left Early at " + timeStamp +"."
                            no =bb
                            print(no)
                            print(type(no))

                            data1 = {
                                "route": "q",
                                "message": message,
                                "language": "english",
                                "flash": 0,
                                "numbers": no,
                            }

                            headers = {
                                "authorization": "OmnbyZilA0HtvwKekDd8JGpM1VR3XsQcNCBx5TWrUYj297F46Etwu4IYkPTpyEM7DJ8Ve2rqZzNo69hX",
                                "Content-Type": "application/json"
                            }

                            response = requests.post(url, headers=headers, json=data1)
                            print(response)
                    elif 600 < in_time and 720 >= in_time: #after 10-12
                        print("ddddddddddd")
                        if count == 0:
                            status = 'Late Coming'
                            sql= "insert into attendance(rno,in_time,in_status,date1) values(%s,%s,%s,%s)"
                            val = (rno, timeStamp, status, date)
                            cursor.execute(sql, val)
                            mydb.commit()
                            url = "https://www.fast2sms.com/dev/bulkV2"

                            message = str(aa)+ "attended Lately at "+ timeStamp +"."
                            no = bb
                            print(no)
                            print(type(no))

                            data1 = {
                                "route": "q",
                                "message": message,
                                "language": "english",
                                "flash": 0,
                                "numbers": no,
                            }

                            headers = {
                                "authorization": "OmnbyZilA0HtvwKekDd8JGpM1VR3XsQcNCBx5TWrUYj297F46Etwu4IYkPTpyEM7DJ8Ve2rqZzNo69hX",
                                "Content-Type": "application/json"
                            }

                            response = requests.post(url, headers=headers, json=data1)
                            print(response)
                        else:
                            s = "Early Out"
                            sq = "update attendance set out_time='%s',out_status='%s' where rno='%s' and date1='%s'" % (
                                timeStamp, s, rno, date)
                            cursor.execute(sq)
                            mydb.commit()
                            url = "https://www.fast2sms.com/dev/bulkV2"

                            message = str(aa)+ "left early at "+timeStamp +"."
                            no = bb
                            print(no)
                            print(type(no))

                            data1 = {
                                "route": "q",
                                "message": message,
                                "language": "english",
                                "flash": 0,
                                "numbers": no,
                            }

                            headers = {
                                "authorization": "OmnbyZilA0HtvwKekDd8JGpM1VR3XsQcNCBx5TWrUYj297F46Etwu4IYkPTpyEM7DJ8Ve2rqZzNo69hX",
                                "Content-Type": "application/json"
                            }

                            response = requests.post(url, headers=headers, json=data1)
                            print(response)

                    elif 720 <= in_time and 960 >= in_time:#12-4
                        print("lllllllllllllllll")
                        # sql="select count(*) from attendance where rno='%s' and date1='%s'"%(rno,date)
                        # x=pd.read_sql_query(sql,mydb)
                        # count=x.values[0][0]
                        if count==0:
                            print("kkkkkkkkkkkkkkk")
                            status = 'Afternoon Come'
                            sql = "insert into attendance(rno,in_time,in_status,date1) values(%s,%s,%s,%s)"
                            val = (rno, timeStamp, status, date)
                            cursor.execute(sql, val)
                            mydb.commit()
                            url = "https://www.fast2sms.com/dev/bulkV2"

                            message = str(aa)+ " attended  Afternoon session at "+timeStamp +"."
                            no = bb
                            print(no)
                            print(type(no))

                            data1 = {
                                "route": "q",
                                "message": message,
                                "language": "english",
                                "flash": 0,
                                "numbers": no,
                            }

                            headers = {
                                "authorization": "OmnbyZilA0HtvwKekDd8JGpM1VR3XsQcNCBx5TWrUYj297F46Etwu4IYkPTpyEM7DJ8Ve2rqZzNo69hX",
                                "Content-Type": "application/json"
                            }

                            response = requests.post(url, headers=headers, json=data1)
                            print(response)
                        else:
                            print("uuuuuuuuuuuuuuuuuu")
                            s="Early Out"
                            sq="update attendance set out_time='%s',out_status='%s' where rno='%s' and date1='%s'"%(timeStamp,s,rno,date)
                            cursor.execute(sq)
                            mydb.commit()
                            url = "https://www.fast2sms.com/dev/bulkV2"

                            message = str(aa)+" left Early at "+timeStamp +"."
                            no =bb
                            print(no)
                            print(type(no))

                            data1 = {
                                "route": "q",
                                "message": message,
                                "language": "english",
                                "flash": 0,
                                "numbers": no,
                            }

                            headers = {
                                "authorization": "OmnbyZilA0HtvwKekDd8JGpM1VR3XsQcNCBx5TWrUYj297F46Etwu4IYkPTpyEM7DJ8Ve2rqZzNo69hX",
                                "Content-Type": "application/json"
                            }

                            response = requests.post(url, headers=headers, json=data1)
                            print(response)
                    else:#after 4

                        print("aaaaaaaaaaaaaaaa")
                        s = "Perfect Out"
                        sq = "update attendance set out_time='%s',out_status='%s' where rno='%s' and date1='%s'" % (timeStamp, s, rno, date)
                        cursor.execute(sq)
                        mydb.commit()
                        url = "https://www.fast2sms.com/dev/bulkV2"
                        message = str(aa)+" fulfield hours and left at "+timeStamp +"."
                        no =bb
                        print(no)
                        print(type(no))

                        data1 = {
                            "route": "q",
                            "message": message,
                            "language": "english",
                            "flash": 0,
                            "numbers": no,
                        }

                        headers = {
                            "authorization": "OmnbyZilA0HtvwKekDd8JGpM1VR3XsQcNCBx5TWrUYj297F46Etwu4IYkPTpyEM7DJ8Ve2rqZzNo69hX",
                            "Content-Type": "application/json"
                        }

                        response = requests.post(url, headers=headers, json=data1)
                        print(response)
                    det=0

            else:
                Id = 'Unknown'
                tt = str(Id)
                # print(tt)
            if (conf > 55):
                noOfFile = len(os.listdir("ImageUnknown")) + 1
                cv2.imwrite(r"ImageUnknown\Image" + str(noOfFile) + ".jpg", im[y:y + h, x:x + w])
            # print("tt:",str(tt))
            # print("x:", str(x))
            # print("y:", str(y))
            # print("font:", str(font))
            cv2.putText(im, str(tt), (x, y + h), font, 1, (255, 255, 255), 2)
        cv2.imshow('im', im)
        if (cv2.waitKey(1) == ord('q')):
            break
    cam.release()
    cv2.destroyAllWindows()
    flash("Attendance taken","success")
    return render_template('index.html')

@app.route('/viewdata', methods=['POST','GET'])
def viewdata():
    if request.method=='POST':
        rno=request.form['rno']
    sql="select * from attendance where rno='%s' "%(rno)
    cursor.execute(sql, mydb)
    data = cursor.fetchall()
    return render_template('viewdata.html',data=data)

if __name__=='__main__':
    app.run(debug=True)

