from flask import Flask, render_template, flash, request, session,send_file
from flask import render_template, redirect, url_for, request
#from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from werkzeug.utils import secure_filename
from datetime import date
import time
import mysql.connector
import yagmail
import cv2
import os
import numpy as np
from PIL import Image,ImageTk
import pandas as pd
import datetime
import time
app = Flask(__name__)
app.config['DEBUG']
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
import datetime

x = datetime.datetime.now()

#print(x.year)
date=x.strftime("%d-%m-%Y")
time1=x.strftime("%X")
@app.route("/")
def homepage():
    return render_template('index1.html')
@app.route("/inbox")
def inbox():
    smailid = session['uname']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from student")
    data = cursor.fetchall()
    return render_template('inbox.html',data=data)
@app.route("/compose")
def compose():
    return render_template('addonlineclass.html')
@app.route("/send")
def send():

    return render_template('newstudent.html')

@app.route("/addstaff")
def addstaff():

    return render_template('newstaff.html')

@app.route("/spam")
def spam():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from onlineclass")
    data = cursor.fetchall()
    return render_template('statusview.html',data=data)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

      username = request.form['uname']
      password = request.form['password']
      session['uname'] = request.form['uname']
      conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
      cursor = conn.cursor()
      cursor.execute("SELECT * from admin where uname='" + username + "' and password='" + password + "'")
      data = cursor.fetchone()
      if data is None:
          return 'Username or Password is wrong'
      else:
          return render_template('inbox.html')
      return render_template('index.html')
@app.route("/addonline", methods=['GET', 'POST'])
def addonline():
    if request.method == 'POST':
        n = request.form['cname']
        msubject = request.form['msubject']
        message = request.form['message']
        classlink = request.form['classlink']
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO onlineclass VALUES ('','" + n + "','" + msubject + "','" + message + "','" + classlink + "')")
        conn.commit()
        conn.close()
        # return 'file register successfully'
        return render_template('inbox.html')
@app.route("/newstudent", methods=['GET', 'POST'])
def newstudent():
    if request.method == 'POST':
        regno = request.form['regno']
        sname = request.form['sname']
        gender = request.form['gender']
        dob = request.form['dob']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        dept = request.form['dept']
        year = request.form['year']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO student VALUES ('','" + regno + "','" + sname + "','" + gender + "','" + dob + "','"+email+"','"+phone+"','"+address+"','"+dept+"','"+year+"')")
        conn.commit()
        conn.close()

        # return 'file register successfully'
        conn1 = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')

        cursor1 = conn1.cursor()
        cursor1.execute("select * from student where regno='" + regno + "'")
        data = cursor1.fetchone()
        if data is None:
            print(data)
        else:
            fid = data[0]
        print(fid)
        cam = cv2.VideoCapture(0)
        cam.set(3, 640)  # set video width
        cam.set(4, 480)  # set video height

        # make sure 'haarcascade_frontalface_default.xml' is in the same folder as this code
        face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # For each person, enter one numeric face id (must enter number start from 1, this is the lable of person 1)
        face_id = fid

        print("\n [INFO] Initializing face capture. Look the camera and wait ...")
        # Initialize individual sampling face count
        count = 0
        while (True):

            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                count += 1

                # Save the captured image into the datasets folder
                cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])

                cv2.imshow('image', img)

            k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= 60:  # Take 30 face sample and stop video
                break
        # Do a bit of cleanup
        print("\n [INFO] Exiting Program and cleanup stuff")
        cam.release()
        cv2.destroyAllWindows()
        path = 'dataset'

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

        def getImagesAndLabels(path):

            imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
            faceSamples = []
            ids = []

            for imagePath in imagePaths:

                PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
                img_numpy = np.array(PIL_img, 'uint8')

                id = int(os.path.split(imagePath)[-1].split(".")[1])
                faces = detector.detectMultiScale(img_numpy)

                for (x, y, w, h) in faces:
                    faceSamples.append(img_numpy[y:y + h, x:x + w])
                    ids.append(id)

            return faceSamples, ids

        print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        faces, ids = getImagesAndLabels(path)
        recognizer.train(faces, np.array(ids))

        # Save the model into trainer/trainer.yml
        recognizer.write('trainer/trainer.yml')  # recognizer.save() worked on Mac, but not on Pi

        # Print the numer of faces trained and end program
        print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute("SELECT * from student")
        data = cursor.fetchall()





        return render_template('inbox.html',data=data)

@app.route("/newstaff", methods=['GET', 'POST'])
def newstaff():
    if request.method == 'POST':
        regno = request.form['regno']
        sname = request.form['sname']
        gender = request.form['gender']
        dob = request.form['dob']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        dept = request.form['dept']
        year = request.form['year']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO staff VALUES ('','" + regno + "','" + sname + "','" + gender + "','" + dob + "','"+email+"','"+phone+"','"+address+"','"+dept+"','"+year+"')")
        conn.commit()
        conn.close()
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute("SELECT * from staff")
        data = cursor.fetchall()
        # return 'file register successfully'
        return render_template('viewstaff.html',data=data)

@app.route("/viewstaff")
def viewstaff():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from staff")
    data = cursor.fetchall()
    # return 'file register successfully'
    return render_template('viewstaff.html',data=data)

@app.route("/register")
def register():
    return render_template('register.html')
@app.route("/aview")
def aview():
    cname = request.args.get('id')
    print(cname)
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from updatestatus1 where cname='" + cname + "'")
    data = cursor.fetchall()
    return render_template('aview.html',data=data)
@app.route("/studlogin")
def studlogin():
    return render_template('studlogin.html')
@app.route("/slogin", methods=['GET', 'POST'])
def slogin():
    if request.method == 'POST':

      username = request.form['uname']
      session['uname']=username

      password = request.form['password']
      session['password'] = password
      session['uname'] = request.form['uname']
      conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
      cursor = conn.cursor()
      cursor.execute("SELECT * from student where regno='" + username + "' and name='" + password + "'")
      data = cursor.fetchone()
      if data is None:
          return 'Username or Password is wrong'
      else:
          conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
          cursor = conn.cursor()
          cursor.execute("SELECT * from onlineclass")
          data = cursor.fetchall()

          return render_template('inbox3.html',data=data)


@app.route("/stflogin", methods=['GET', 'POST'])
def stflogin():
    if request.method == 'POST':

      username = request.form['uname']
      session['suname']=username

      password = request.form['password']
      session['password'] = password
      session['uname'] = request.form['uname']
      conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
      cursor = conn.cursor()
      cursor.execute("SELECT * from staff where regno='" + username + "' and name='" + password + "'")
      data = cursor.fetchone()
      if data is None:
          return 'Username or Password is wrong'
      else:
          conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
          cursor = conn.cursor()
          cursor.execute("SELECT * from onlineclass")
          data = cursor.fetchall()

          return render_template('staffhome.html',data=data)






@app.route("/attenclass")
def attenclass():
    # !/usr/bin/env python
    cname=request.args.get('id')
    session['cname']=cname
    regno=session['uname']
    uname=session['password']
    now = time.time()  ###For calculate seconds of video
    future = now + 300


    my_list = ['']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("select * from student")
    data = cursor.fetchall()
    print(data)
    for data1 in data:
        my_list.append(data1[2])
    print(my_list)

    import cv2
    import numpy as np
    import os

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')  # load trained model
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);

    font = cv2.FONT_HERSHEY_SIMPLEX

    # iniciate id counter, the number of persons you want to include
    id = 0  # two persons (e.g. Jacob, Jack)

    names = my_list  # key in names, start from the second place, leave first empty

    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)  # set video widht
    cam.set(4, 480)  # set video height

    # Define min window size to be recognized as a face
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)
    start = time.time()

    while True:

        ret, img = cam.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 60):
                id1 = id
                print(id)

                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))


            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(img, str(), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)
        print(id)
        if time.time() > future:
            break

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break

    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    end = time.time()


    millis =(end-start) * 10**3
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (millis / (1000 * 60 * 60)) % 24
    if minutes>=3:
        st="Full Present"
    elif minutes>=2:
        st = "Full Present"
    elif minutes<2:
        st = "Absent"


    cursor1 = conn.cursor()
    cursor1.execute("select * from student where name='" + str(id) + "'")
    data2 = cursor1.fetchone()
    if data2 is None:
        return "Unknown User"
    else:

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO updatestatus1 VALUES ('','" + str(cname) + "','" + str(regno) + "','" + str(
                uname) + "','"+str(minutes)+"','"+str(st)+"','')")
        conn.commit()
        conn.close()
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor1 = conn.cursor()
        cursor1.execute("SELECT * FROM questions where subject='" + cname + "' ORDER BY RAND( ) LIMIT 5")
        data2 = cursor1.fetchall()
        print(data2)

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute("select * from student where regno='"+str(regno)+"'")
        data = cursor.fetchone()
        #print(data)
        for data1 in data:
            email=data[5]

        import yagmail
        mail = 'testsam360@gmail.com';
        password = 'rddwmbynfcbgpywf';
        # list of email_id to send the mail

        body = "Alert Thanks for attending the session your attendance has been recorded"
        yag = yagmail.SMTP(mail, password)
        yag.send(to=email, subject="Alert...!", contents=body)

        return render_template("ans.html", data=data2)





@app.route("/studhome")
def studhome():


          conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
          cursor = conn.cursor()
          cursor.execute("SELECT * from onlineclass")
          data = cursor.fetchall()

          return render_template('inbox3.html',data=data)


@app.route("/search",methods=['GET', 'POST'])
def search():
    username = request.form['status']
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from updatestatus1 where sstatus='" +username+"'")
    data = cursor.fetchall()

    return render_template('aview.html',data=data)


@app.route("/stafflogin")
def stafflogin():
    return render_template('stafflogin.html')

@app.route("/addquestion")
def addquestion():

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from onlineclass")
    data = cursor.fetchall()

    return render_template('addquestion.html',data=data)

@app.route("/newquest",methods=['GET','POST'])
def newquest():
    if request.method == 'POST':

        subject = request.form['subject']
        question = request.form['question']
        ans1 = request.form['ans1']
        ans2 = request.form['ans2']
        ans3 = request.form['ans3']
        ans4 = request.form['ans4']
        ans = request.form['anstrue']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute(
            "insert into questions values('','" + subject + "','" + question + "','" + ans1 + "','" + ans2 + "','" + ans3 + "','" + ans4 + "','" + ans + "')")
        conn.commit()
        conn.close()
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor = conn.cursor()
        cursor.execute("SELECT * from questions")
        data = cursor.fetchall()

        return render_template("viewquest.html",data=data)
@app.route("/staffhome")
def staffhome():

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from onlineclass")
    data = cursor.fetchall()

    return render_template('staffhome.html',data=data)

@app.route("/viewquest")
def viewquest():

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
    cursor = conn.cursor()
    cursor.execute("SELECT * from questions")
    data = cursor.fetchall()

    return render_template('viewquest.html',data=data)



@app.route("/ans",methods=['GET','POST'])
def ans():
    if request.method == 'POST':
        regno=session['uname']
        cname=session['cname']
        qs1 = request.form['qs1']
        an1 = request.form['an1']
        q1 = request.form['q1']
        qs2 = request.form['qs2']
        an2 = request.form['an2']
        q2 = request.form['q2']
        qs3 = request.form['qs3']
        an3 = request.form['an3']
        q3 = request.form['q3']
        qs4 = request.form['qs4']
        an4 = request.form['an4']
        q4 = request.form['q4']
        qs5 = request.form['qs5']
        an5 = request.form['an5']
        q5 = request.form['q5']
        if q1==an1:
            qn1=1;
        else:
            qn1=0
        if q2==an2:
            qn2=1;
        else:
            qn2=0
        if q3==an3:
            qn3=1;
        else:
            qn3=0
        if q4==an4:
            qn4=1;
        else:
            qn4=0
        if q5==an5:
            qn5=1;
        else:
            qn5=0

        rg=qn1+qn2+qn3+qn4+qn5
        i=5;

        conn1 = mysql.connector.connect(user='root', password='', host='localhost', database='onlineclass')
        cursor1= conn1.cursor()
        cursor1.execute("update updatestatus1 set ans='"+str(rg)+"' where cname='"+cname+"' and regno='"+regno+"'")

        conn1.commit()
        conn1.close()

        return render_template("inbox3.html")










if __name__ == '__main__':
    app.run(debug=True, use_reloader=True,host='0.0.0.0')