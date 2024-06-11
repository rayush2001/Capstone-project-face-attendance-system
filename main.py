import tkinter as tk
from tkinter import *
import cv2 
from tkinter import messagebox
import csv
import os
import numpy as np
from PIL import Image,ImageTk
import pandas as pd
import datetime
import time


#Functions for back button on register student and mark attendance
def back_to_main_page(win):
    win.destroy()
    open_after_login()

#Functions for mark attendance
def del_errsc2():
        errsc2.destroy()
def err_screen1():
            global errsc2
            errsc2 = tk.Tk()
            errsc2.geometry('330x100')
            errsc2.title('Warning!!')
            errsc2.configure(background='snow')
            Label(errsc2, text='Please enter Student & Reg. no.!!!', fg='red', bg='white',
                    font=('times', 16, ' bold ')).pack()
            Button(errsc2, text='OK', command=del_errsc2, fg="black", bg="lawn green", width=9, height=1,
                    activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

def subjectchoose():
    def Fillattendances():
        sub=tx.get()
        now = time.time()  # For calculate seconds of video
        future = now + 20
        if time.time() < future:
            if sub == '':
                err_screen1()
            else:
                recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
                # recognizer.read("TrainingImageLabel/Trainner.yml")
                try:
                    recognizer.read("TrainingImageLabel/Trainner.yml")
                except:
                    e = 'Model not found,Please train model'
                    Notifica.configure(text=e, bg="red", fg="black", width=33, font=('times', 15, 'bold'))
                    Notifica.place(x=20, y=250)

                harcascadePath = "haarcascade_frontalface_default.xml"
                faceCascade = cv2.CascadeClassifier(harcascadePath)
                df = pd.read_csv("StudentDetails/StudentDetails.csv")
                cam = cv2.VideoCapture(0)
                font = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ['Reg_no.', 'Name', 'Date', 'Time']
                attendance = pd.DataFrame(columns=col_names)
                while True:
                    ret, im = cam.read()
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        global Id

                        Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                        if (conf <70):
                            print(conf)
                            global Subject
                            global aa
                            global date
                            global timeStamp
                            Subject = tx.get()
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                            aa = df.loc[df['Reg_no.'] == Id]['Name'].values
                            global tt
                            tt = str(Id) + "-" + aa
                            En = '15624031' + str(Id)
                            attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 0), 7)
                            cv2.putText(im, str(tt), (x + h, y), font, 1, (255, 255, 0,), 4)

                        else:
                            Id = 'Unknown'
                            tt = str(Id)
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                            cv2.putText(im, str(tt), (x + h, y), font, 1, (0, 25, 255), 4)
                    if time.time() > future:
                        break

                    attendance = attendance.drop_duplicates(['Reg_no.'], keep='first')
                    cv2.imshow('Filling attendance..', im)
                    key = cv2.waitKey(30) & 0xff
                    if key == 27:
                        break

                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                Hour, Minute, Second = timeStamp.split(":")
                fileName = "Attendance/" + Subject + "_" + date + "_" + Hour + "-" + Minute + "-" + Second + ".csv"
                attendance = attendance.drop_duplicates(['Reg_no.'], keep='first')
                print(attendance)
                attendance.to_csv(fileName, index=False)

                ##Create table for Attendance
                date_for_DB = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
                DB_Table_name = str( Subject + "_" + date_for_DB + "_Time_" + Hour + "_" + Minute + "_" + Second)
                import pymysql.connections

                ###Connect to the database
                try:
                    global mycursor
                    connection = pymysql.connect(host='localhost', user='root', password='', db='Face_reco_fill')
                    mycursor = connection.cursor()
                except Exception as e:
                    print(e)

                sql = "CREATE TABLE " + DB_Table_name + """
                (ID INT NOT NULL AUTO_INCREMENT,
                 ENROLLMENT varchar(100) NOT NULL,
                 NAME VARCHAR(50) NOT NULL,
                 DATE VARCHAR(20) NOT NULL,
                 TIME VARCHAR(20) NOT NULL,
                     PRIMARY KEY (ID)
                     );
                """
                ####Now enter attendance in Database
                insert_data =  "INSERT INTO " + DB_Table_name + " (ID,REG_NO,NAME,DATE,TIME) VALUES (0, %s, %s, %s,%s)"
                VALUES = (str(Id), str(aa), str(date), str(timeStamp))
                try:
                    mycursor.execute(sql)  ##for create a table
                    mycursor.execute(insert_data, VALUES)##For insert data into table
                except Exception as ex:
                    print(ex)  #

                M = 'Attendance filled Successfully'
                Notifica.configure(text=M, bg="Green", fg="white", width=33, font=('times', 15, 'bold'))
                Notifica.place(x=20, y=250)

                cam.release()
                cv2.destroyAllWindows()

                import csv
                import tkinter
                root = tkinter.Tk()
                root.title("Attendance of " + Subject)
                root.configure(background='snow')
                cs = '' + fileName
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            label = tkinter.Label(root, width=8, height=1, fg="black", font=('times', 15, ' bold '),
                                                  bg="lawn green", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                root.mainloop()
                print(attendance)

    #windo is frame for subject chooser
    windo = tk.Tk()
    windo.title("Enter subject name...")
    windo.geometry('580x320')
    windo.configure(background='snow')
    Notifica = tk.Label(windo, text="Attendance filled Successfully", bg="Green", fg="white", width=33,
                            height=2, font=('times', 15, 'bold'))

    def Attf():
       import os
       import glob
       import csv
       
       def list_of_mark_attendance(first_csv):
            import tkinter
            root = tk.Tk()
            root.title("List of Mark attendance")
            root.configure(background='snow')
            cs = first_csv
            with open(cs, newline="") as file:
                reader = csv.reader(file)
                r = 0
                for col in reader:
                    c = 0
                    for row in col:
                        label = tk.Label(root, width=8, height=1, fg="black", font=('times', 15, ' bold '),
                                                  bg="lawn green", text=row, relief=tkinter.RIDGE)
                        label.grid(row=r, column=c)
                        c += 1
                    r += 1
                root.mainloop()

       csv_pattern = "*.csv"
       folder_path = os.path.join(os.getcwd(), "./Attendance")
       first_csv = glob.glob(os.path.join(folder_path, csv_pattern))[0]
       list_of_mark_attendance(first_csv)
       

    attf = tk.Button(windo,  text="Check Sheets",command=Attf,fg="black"  ,bg="lawn green"  ,width=10  ,height=1 ,activebackground = "Red" ,font=('times', 14, ' bold '))
    attf.place(x=430, y=255)

    sub = tk.Label(windo, text="Enter Subject", width=15, height=2, fg="black", bg="white", font=('times', 15, ' bold '))
    sub.place(x=30, y=100)

    tx = tk.Entry(windo, width=20, bg="white", fg="black", font=('times', 23, ' bold '))
    tx.place(x=250, y=105)

    fill_a = tk.Button(windo, text="Fill Attendance", fg="black",command=Fillattendances, bg="gray80", width=20, height=2,
                       activebackground="Red", font=('times', 15, ' bold '))
    fill_a.place(x=250, y=160)
    windo.mainloop()

def manually_fill():
    global sb
    sb = tk.Tk()
    sb.title("Please enter subject Name :-")
    sb.geometry('580x320')
    sb.configure(background='snow')

    def err_screen_for_subject():

        def ec_delete():
            ec.destroy()
        global ec
        ec = tk.Tk()
        ec.geometry('300x100')
        ec.title('Warning!!')
        ec.configure(background='snow')
        Label(ec, text='Please enter your subject name!!!', fg='red', bg='white', font=('times', 16, ' bold ')).pack()
        Button(ec, text='OK', command=ec_delete, fg="black", bg="lawn green", width=9, height=1, activebackground="Red",
               font=('times', 15, ' bold ')).place(x=90, y=50)

    def fill_attendance():
        ts = time.time()
        Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")
        ####Creatting csv of attendance

        ##Create table for Attendance
        date_for_DB = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
        #global cursor
        global subb
        subb=SUB_ENTRY.get()
        DB_table_name = str(subb + "_" + Date + "_Time_" + Hour + "_" + Minute + "_" + Second)

        import pymysql.connections
        global mycursor

        ###Connect to the database
        try:
            global mycursor
            connection = pymysql.connect(host='localhost', user='root', password='root', db='manually_fill_attendance')
            mycursor = connection.cursor()
        except Exception as e:
            print(e)

        sql = "CREATE TABLE " + DB_table_name + """
                        (ID INT NOT NULL AUTO_INCREMENT,
                         ENROLLMENT varchar(100) NOT NULL,
                         NAME VARCHAR(50) NOT NULL,
                         DATE VARCHAR(20) NOT NULL,
                         TIME VARCHAR(20) NOT NULL,
                             PRIMARY KEY (ID)
                             );
                        """

        try:
            mycursor.execute(sql)  ##for create a table
        except Exception as ex:
            print(ex)  #

        if subb=='':
            err_screen_for_subject()
        else:
            sb.destroy()
            MFW = tk.Tk()
            MFW.title("Manually attendance of "+ str(subb))
            MFW.geometry('880x470')
            MFW.configure(background='snow')

            def del_errsc2():
                errsc2.destroy()

            def err_screen1():
                global errsc2
                errsc2 = tk.Tk()
                errsc2.geometry('330x100')
                errsc2.title('Warning!!')
                errsc2.configure(background='snow')
                Label(errsc2, text='Please enter Student & Reg. no.!!!', fg='red', bg='white',
                      font=('times', 16, ' bold ')).pack()
                Button(errsc2, text='OK', command=del_errsc2, fg="black", bg="lawn green", width=9, height=1,
                       activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

            def testVal(inStr, acttyp):
                if acttyp == '1':  # insert
                    if not inStr.isdigit():
                        return False
                return True

            ENR = tk.Label(MFW, text="Enter Reg. no.", width=15, height=2, fg="black", bg="white",
                           font=('times', 15, ' bold '))
            ENR.place(x=30, y=100)

            STU_NAME = tk.Label(MFW, text="Enter Student name", width=15, height=2, fg="black", bg="white",
                                font=('times', 15, ' bold '))
            STU_NAME.place(x=30, y=200)

            global ENR_ENTRY
            ENR_ENTRY = tk.Entry(MFW, width=20,validate='key', bg="white", fg="black", font=('times', 23, ' bold '))
            ENR_ENTRY['validatecommand'] = (ENR_ENTRY.register(testVal), '%P', '%d')
            ENR_ENTRY.place(x=290, y=105)

            def remove_enr():
                ENR_ENTRY.delete(first=0, last=22)

            STUDENT_ENTRY = tk.Entry(MFW, width=20, bg="white", fg="black", font=('times', 23, ' bold '))
            STUDENT_ENTRY.place(x=290, y=205)

            def remove_student():
                STUDENT_ENTRY.delete(first=0, last=22)

            ####get important variable
            def enter_data_DB():
                ENROLLMENT = ENR_ENTRY.get()
                STUDENT = STUDENT_ENTRY.get()
                if ENROLLMENT=='':
                    err_screen1()
                elif STUDENT=='':
                    err_screen1()
                else:
                    time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    Hour, Minute, Second = time.split(":")
                    Insert_data = "INSERT INTO " + DB_table_name + " (ID,ENROLLMENT,NAME,DATE,TIME) VALUES (0, %s, %s, %s,%s)"
                    VALUES = (str(ENROLLMENT), str(STUDENT), str(Date), str(time))
                    try:
                        mycursor.execute(Insert_data, VALUES)
                    except Exception as e:
                        print(e)
                    ENR_ENTRY.delete(first=0, last=22)
                    STUDENT_ENTRY.delete(first=0, last=22)

            def create_csv():
                import csv
                mycursor.execute("select * from " + DB_table_name + ";")
                csv_name='./Manually Attendance/'+DB_table_name+'.csv'
                with open(csv_name, "w") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([i[0] for i in mycursor.description])  # write headers
                    csv_writer.writerows(mycursor)
                    O="CSV created Successfully"
                    Notifi.configure(text=O, bg="Green", fg="white", width=33, font=('times', 19, 'bold'))
                    Notifi.place(x=180, y=380)
                import csv
                import tkinter
                root = tkinter.Tk()
                root.title("Attendance of " + subb)
                root.configure(background='snow')
                with open(csv_name, newline="") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            label = tkinter.Label(root, width=13, height=1, fg="black", font=('times', 13, ' bold '),
                                                  bg="lawn green", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                root.mainloop()

            Notifi = tk.Label(MFW, text="CSV created Successfully", bg="Green", fg="white", width=33,
                                height=2, font=('times', 19, 'bold'))


            c1ear_enroll = tk.Button(MFW, text="Clear", command=remove_enr, fg="black", bg="gray71", width=10,
                                     height=1,
                                     activebackground="Red", font=('times', 15, ' bold '))
            c1ear_enroll.place(x=690, y=100)

            c1ear_student = tk.Button(MFW, text="Clear", command=remove_student, fg="black", bg="gray71", width=10,
                                      height=1,
                                      activebackground="Red", font=('times', 15, ' bold '))
            c1ear_student.place(x=690, y=200)

            DATA_SUB = tk.Button(MFW, text="Enter Data",command=enter_data_DB, fg="black", bg="lime green", width=20,
                                 height=2,
                                 activebackground="Red", font=('times', 15, ' bold '))
            DATA_SUB.place(x=170, y=300)

            MAKE_CSV = tk.Button(MFW, text="Convert to CSV",command=create_csv, fg="black", bg="lightgoldenrod1", width=20,
                                 height=2,
                                 activebackground="Red", font=('times', 15, ' bold '))
            MAKE_CSV.place(x=570, y=300)

           
            MFW.mainloop()

    def Attf():
        import os
        import glob
        import csv

        def list_of_mark_attendance(first_csv):
                import tkinter
                root = tk.Tk()
                root.title("List of Mark attendance")
                root.configure(background='snow')
                cs = first_csv
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    r = 0
                    for col in reader:
                        c = 0
                        for row in col:
                            label = tk.Label(root, width=8, height=1, fg="black", font=('times', 15, ' bold '),
                                                  bg="lawn green", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                    root.mainloop()

                csv_pattern = "*.csv"
                folder_path = os.path.join(os.getcwd(), "./Attendance/Manually Attendance")
                first_csv = glob.glob(os.path.join(folder_path, csv_pattern))[0]
                list_of_mark_attendance(first_csv)

    SUB = tk.Label(sb, text="Enter Subject", width=15, height=2, fg="black", bg="white", font=('times', 15, ' bold '))
    SUB.place(x=30, y=100)

    global SUB_ENTRY

    SUB_ENTRY = tk.Entry(sb, width=20, bg="white", fg="black", font=('times', 23, ' bold '))
    SUB_ENTRY.place(x=250, y=105)

    fill_manual_attendance = tk.Button(sb, text="Fill Attendance",command=fill_attendance, fg="black", bg="gray80", width=20, height=2,
                       activebackground="Red", font=('times', 15, ' bold '))
    fill_manual_attendance.place(x=250, y=160)

    attf = tk.Button(sb, text="Check Sheets",command=Attf,fg="black" ,bg="lawn green" ,width=10 ,height=1 ,activebackground = "Red" ,font=('times', 14, ' bold '))
    attf.place(x=400, y=280)
    sb.mainloop()

# Function after clicking Register student or Mark attendance
def Mark_attendance_page(win):
    win.destroy()
    win = tk.Tk()
    win.title("Face Attendance using Machine Learning")
    win.geometry('1970x920')

    message = tk.Label(win, text=title, fg="black", font=('times', 30, 'bold'))
    message.place(x=500, y=20)

    AA = tk.Button(win, text="Automatic Attendance",fg="black",command=subjectchoose  ,bg="alice blue"  ,width=20  ,height=3, activebackground = "Red" ,font=('times', 15, ' bold '))
    AA.place(x=690, y=300)

    manualfill = tk.Button(win, text="Manually Fill Attendance", command=manually_fill  ,fg="black"  ,bg="thistle"  ,width=20  ,height=3, activebackground = "Red" ,font=('times', 15, ' bold '))
    manualfill.place(x=690, y=400)

    backrs = tk.Button(win, text="Back",command=lambda: back_to_main_page(win), fg="black",bg="khaki1"  ,width=20  ,height=3, activebackground = "Red" ,font=('times', 15, ' bold '))
    backrs.place(x=690, y=500)
    #win.protocol("WM_DELETE_WINDOW", on_closing)
    win.mainloop()

def student_register(win):
    win.destroy()
    win = tk.Tk()
    win.title("Face Attendance using Machine Learning")
    win.geometry('1970x920')
    def del_sc1():
        sc1.destroy()
    def err_screen():
        global sc1
        sc1 = tk.Tk()
        sc1.geometry('300x100')
        sc1.title('Warning!!')
        sc1.configure(background='snow')
        te= tk.Label(sc1,text='Enrollment & Name required!!!',fg='red',bg='white',font=('times', 16, ' bold '))
        te.pack()
        bu= tk.Button(sc1,text='OK',command=del_sc1,fg="black"  ,bg="lawn green"  ,width=9  ,height=1, activebackground = "Red" ,font=('times', 15, ' bold '))
        bu.place(x=90,y= 50)

    def take_img():
        l1 = txt.get()
        l2 = txt2.get()
        if l1 == '':
            err_screen()
        elif l2 == '':
            err_screen()
        else:
            try:
                cam = cv2.VideoCapture(0)
                detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
                Enrollment = txt.get()
                Name = txt2.get()
                sampleNum = 0
                while (True):
                    ret, img = cam.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, 1.3, 5)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        # incrementing sample number
                        sampleNum = sampleNum + 1
                        # saving the captured face in the dataset folder
                        cv2.imwrite("TrainingImage/ " + Name + "." + Enrollment + '.' + str(sampleNum) + ".jpg",
                                    gray[y:y + h, x:x + w])
                        cv2.imshow('Frame', img)
                    # wait for 100 miliseconds
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    # break if the sample number is morethan 100
                    elif sampleNum > 70:
                        break
                cam.release()
                cv2.destroyAllWindows()
                ts = time.time()
                Date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                row = [Enrollment, Name, Date, Time]
                with open('StudentDetails/StudentDetails.csv', 'a+') as csvFile:
                    writer = csv.writer(csvFile, delimiter=',')
                    writer.writerow(row)
                    csvFile.close()
                res = "Images Saved for Enrollment : " + Enrollment + " Name : " + Name
                Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
                Notification.place(x=250, y=400)
            except FileExistsError as F:
                f = 'Student Data already exists'
                Notification.configure(text=f, bg="Red", width=21)
                Notification.place(x=450, y=400)

   #For train the model
    def trainimg():
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        global detector
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        try:
            global faces,Id
            faces, Id = getImagesAndLabels("TrainingImage")
        except Exception as e:
            l='please make "TrainingImage" folder & put Images'
            Notification.configure(text=l, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
            Notification.place(x=350, y=400)

        recognizer.train(faces, np.array(Id))
        try:
            recognizer.save("TrainingImageLabel/Trainner.yml")
        except Exception as e:
            q='Please make "TrainingImageLabel" folder'
            Notification.configure(text=q, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
            Notification.place(x=350, y=400)

        res = "Model Trained"  # +",".join(str(f) for f in Id)
        Notification.configure(text=res, bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
        Notification.place(x=250, y=400)
        
    def getImagesAndLabels(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        # create empth face list
        faceSamples = []
        # create empty ID list
        Ids = []
        # now looping through all the image paths and loading the Ids and the images
        for imagePath in imagePaths:
            # loading the image and converting it to gray scale
            pilImage = Image.open(imagePath).convert('L')
            # Now we are converting the PIL image into numpy array
            imageNp = np.array(pilImage, 'uint8')
            # getting the Id from the image
            Id = int(os.path.split(imagePath)[-1].split(".")[1])
            # extract the face from the training image sample
            faces = detector.detectMultiScale(imageNp)
            # If a face is there then append that in the list as well as Id of it
            for (x, y, w, h) in faces:
                faceSamples.append(imageNp[y:y + h, x:x + w])
                Ids.append(Id)
        return faceSamples, Ids
    
    #Function to check the register student
    def check_register_student():
        win = tk.Tk()
        win.title("Login")
        win.geometry('880x420')
        win.configure(background='snow')

        def log_in():
            username = un_entr.get()
            password = pw_entr.get()

            if username == 'admin' :
                if password == 'admin':
                    win.destroy()
                    import csv
                    import tkinter
                    root = tkinter.Tk()
                    root.title("Student Details")
                    root.configure(background='snow')

                    cs = './StudentDetails/StudentDetails.csv'
                    with open(cs, newline="") as file:
                        reader = csv.reader(file)
                        r = 0

                        for col in reader:
                            c = 0
                            for row in col:
                                label = tkinter.Label(root, width=8, height=1, fg="black", font=('times', 15, ' bold '),
                                                  bg="lawn green", text=row, relief=tkinter.RIDGE)
                                label.grid(row=r, column=c)
                                c += 1
                            r += 1
                    root.mainloop()
                else:
                    valid = 'Incorrect ID or Password'
                    Nt.configure(text=valid, bg="red", fg="black", width=38, font=('times', 19, 'bold'))
                    Nt.place(x=120, y=350)

            else:
                valid ='Incorrect ID or Password'
                Nt.configure(text=valid, bg="red", fg="black", width=38, font=('times', 19, 'bold'))
                Nt.place(x=120, y=350)


        Nt = tk.Label(win, text="Attendance filled Successfully", bg="Green", fg="white", width=40,
                    height=2, font=('times', 19, 'bold'))
        # Nt.place(x=120, y=350)

        un = tk.Label(win, text="Enter username", width=15, height=2, fg="black", bg="white",
                    font=('times', 15, ' bold '))
        un.place(x=30, y=50)

        pw = tk.Label(win, text="Enter password", width=15, height=2, fg="black", bg="white",
                  font=('times', 15, ' bold '))
        pw.place(x=30, y=150)

        def c00():
            un_entr.delete(first=0, last=22)

        un_entr = tk.Entry(win, width=20, bg="white", fg="black", font=('times', 23, ' bold '))
        un_entr.place(x=290, y=55)

        def c11():
            pw_entr.delete(first=0, last=22)

        pw_entr = tk.Entry(win, width=20,show="*", bg="white", fg="black", font=('times', 23, ' bold '))
        pw_entr.place(x=290, y=155)

        c0 = tk.Button(win, text="Clear", command=c00, fg="black", bg="gray71", width=10, height=1,
                            activebackground="Red", font=('times', 15, ' bold '))
        c0.place(x=690, y=55)

        c1 = tk.Button(win, text="Clear", command=c11, fg="black", bg="gray71", width=10, height=1,
                    activebackground="Red", font=('times', 15, ' bold '))
        c1.place(x=690, y=155)

        Login = tk.Button(win, text="Login", fg="black", bg="gray80", width=20,
                       height=2,
                       activebackground="Red",command=log_in, font=('times', 15, ' bold '))
        Login.place(x=310, y=250)
        win.mainloop()
    
    message = tk.Label(win, text=title, fg="black", font=('times', 30, 'bold'))
    message.place(x=500, y=20)

    lbl = tk.Label(win, text="Enter Reg.no.:", width=15, height=3, fg="black", bg="white", font=('times', 15, ' bold '))
    lbl.place(x=380, y=230)

    def testVal(inStr,acttyp):
        if acttyp == '1': #insert
            if not inStr.isdigit():
                return False
        return True

    
    Notification = tk.Label(win, text="All things good", bg="Green", fg="white", width=15,
                      height=3, font=('times', 17, 'bold'))
    txt = tk.Entry(win, validate="key", width=20, bg="white", fg="green", font=('times', 25, ' bold '))
    txt['validatecommand'] = (txt.register(testVal),'%P','%d')
    txt.place(x=650, y=250)

    bl2 = tk.Label(win, text="Enter Name:", width=15, fg="black", bg="white", height=3, font=('times', 15, ' bold '))
    bl2.place(x=380, y=330)

    txt2 = tk.Entry(win, width=20, bg="white", fg="green", font=('times', 25, ' bold '))
    txt2.place(x=650, y=350)
    takeImg = tk.Button(win, text="Take Images",command=take_img,fg="black"  ,bg="pale green"  ,width=20  ,height=3, activebackground = "Red" ,font=('times', 15, ' bold '))
    takeImg.place(x=350, y=500)

    trainImg = tk.Button(win, text="Train Images",command=trainimg,fg="black",bg="lightpink"  ,width=20  ,height=3, activebackground = "Red" ,font=('times', 15, ' bold '))
    trainImg.place(x=670, y=500)

    checkrs = tk.Button(win, text="Check Register student",command=check_register_student,fg="black",bg="lightblue1"  ,width=20  ,height=3, activebackground = "Red" ,font=('times', 15, ' bold '))
    checkrs.place(x=670, y=610)

    backrs = tk.Button(win, text="Back",command=lambda: back_to_main_page(win), fg="black",bg="khaki1"  ,width=20  ,height=3, activebackground = "Red" ,font=('times', 15, ' bold '))
    backrs.place(x=970, y=500)
    #win.protocol("WM_DELETE_WINDOW", on_closing)
    win.mainloop()

# Functions after login page(i.e main page)
def verify_login(username, password):
    if username == "admin" and password == "admin":
        return True
    else:
        return False

def login_clicked():
    username = un_entr.get()
    password = pw_entr.get()

    if verify_login(username, password):
        messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
        win.destroy()  # Destroy current login window
        open_after_login()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def open_after_login():
    win = tk.Tk()
    win.title("Face Attendance using Machine Learning")
    win.geometry('1970x920')

    message = tk.Label(win, text=title, fg="black", font=('times', 30, 'bold'))
    message.place(x=500, y=20)

    message = tk.Label(win, text="Welcome, user", fg="black", font=('times', 20, 'bold'))
    message.place(x=680, y=100)
    mark = tk.Button(win, text="Mark Attendance",command=lambda:Mark_attendance_page(win),fg="black"  ,bg="gray80"  ,width=20  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
    mark.place(x=660, y=200)
    register = tk.Button(win, text="Register student",command=lambda:student_register(win),fg="black"  ,bg="gray80"  ,width=20  ,height=2, activebackground = "Red" ,font=('times', 15, ' bold '))
    register.place(x=660, y=300)
    #win.protocol("WM_DELETE_WINDOW", on_closing)
    win.mainloop()


def on_closing():
    from tkinter import messagebox
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        win.destroy()

#Login page
title = "Real-Time Face Attendance System "
win = tk.Tk()
win.title("Face Attendance using Machine Learning")
win.geometry('1970x920')
# win.configure(bg='#34495E')

message = tk.Label(win, text= title, fg="black", font=('times', 30, 'bold'))
message.place(x=500, y=20)

admin = tk.Label(win, text="Admin Login",width=15, height=2, fg="black", font=('times', 20, ' bold '))
admin.place(x=625,y=100)

un = tk.Label(win, text="Enter username:", width=15, height=2, fg="black", font=('times', 9, ' bold '))
un.place(x=600, y=200)

pw = tk.Label(win, text="Enter password:", width=15, height=2, fg="black", font=('times', 9, ' bold '))
pw.place(x=600, y=300)

un_entr = tk.Entry(win, width=20, bg="white", fg="black", font=('times', 23, ' bold '))
un_entr.place(x=600, y=250)

pw_entr = tk.Entry(win, width=20, show="*", bg="white", fg="black", font=('times', 23, ' bold '))
pw_entr.place(x=600, y=350)

lg = tk.Button(win, text="Login", width=10, height=2, fg="white", bg="#FF9912", font=('time', 12, 'bold'), command=login_clicked)
lg.place(x=700, y=400)
win.protocol("WM_DELETE_WINDOW", on_closing)
win.mainloop()