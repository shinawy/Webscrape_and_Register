from flask import Flask,render_template,request, redirect,url_for
from datetime import date
from flask_mysqldb import MySQL

app =Flask(__name__)

#configuring the informations of the database

app.config['MYSQL_HOST']="sql2.freemysqlhosting.net"
app.config['MYSQL_USER']='sql2378962'
app.config['MYSQL_PASSWORD']="mP7%pU2*"
app.config['MYSQL_DB']="sql2378962"

mysql=MySQL(app)
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        user=request.form
        print(user)
        id=user['id']
        passwd=user["password"]
        if id == "":
            return "Enter your id"
        if passwd == "":
            return "Enter the Password"
        else:
            cur=mysql.connection.cursor()
            users=cur.execute("select * from users where ID='"+id+"' and passwd='"+passwd+"'")
            userdetails=cur.fetchall()
            cur.close()
            print("users are ",users)
            print("userdetails", userdetails)
            if users==0:
                return "You're not registered, Kindly go to the Registrar to add your credentials"
            else:
                if userdetails[0][2]=="admin":
                    return redirect('/admin')
                elif userdetails[0][2]=="student":
                    return redirect(url_for('student',id=id))

    return render_template("index.html")

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method=='POST':
        admin=request.form
        StudentID=admin['StudentID']
        deptCode = admin['deptCode']
        courseNum = admin['courseNum']
        letterGrade = admin['letterGrade']
        semester = admin['semester']
        year = admin['year']
        if StudentID=='':
            return "StudentID field is Empty"
        if deptCode=='':
            return "deptCode field is Empty"
        if courseNum=='':
            return "courseNum field is Empty"
        if letterGrade=='':
            return "letterGrade field is Empty"
        if semester=='':
            return "semester field is Empty"
        if year=='':
            return "year field is Empty"
        cur = mysql.connection.cursor()
        flag = cur.execute(" select * from Student where StudentID='" + StudentID +"' ")
        if flag==0:
            return "StudentID does not exist"
        flag = cur.execute(" select * from Course where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        if flag == 0:
            return "Course does not exist"
        letterGradelist=['A','A-','B+','B','B-','C+','C','C-','D+','D','F']
        count=0
        for item in letterGradelist:
            if (letterGrade!=item):
                count=count+1
            else:
                break
        if count==11:
            return "LetterGrade is not Valid"
        count=0
        semesterlist = ['Fall', 'Spring', 'Winter', 'Summer']
        for item  in semesterlist:
            if (semester!=item):
                count=count+1
            else:
                break
        if (count==4):
            return "Semester is not Valid, Make sure the first letter is an uppercase"
        try:
            if ((int(year)<2000) or (int(year)>2021)):
                return "Year is not Valid"
        except:
            return "Year is not Valid"
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO CourseStudent values(%s,%s,%s,%s,%s,%s)", (StudentID,deptCode,courseNum,letterGrade,semester,year))
        cur.connection.commit()
        cur.close()
        return "Added Successfully"
    return render_template("admin.html")

@app.route('/student/<id>', methods=['GET','POST'])
def student(id):
    cur=mysql.connection.cursor()
    studentinfo=cur.execute("select * from Student where StudentId='"+id+"'")
    studentinfo=cur.fetchall()
    cur.close()
    if request.method=='POST':
        choice=request.form
        finalchoice=choice["choice"]
        if int(finalchoice)==1:
            return redirect('/viewreviews')
        elif int(finalchoice)==2:
            return redirect(url_for('postReviews',id=id))
        elif int(finalchoice)==3:
            return redirect('/viewcourseinfo')
        elif int(finalchoice)==4:
            return redirect(url_for('works',id=id))
        elif int(finalchoice)==5:
            return redirect(url_for('degreeworks',id=id))
        else:
            return "Please choose Number between 1-5 Representing your Choice"

    stringgpa=str(studentinfo[0][2])
    return render_template("student.html",id=studentinfo[0][0],name=studentinfo[0][1],gpa= studentinfo[0][2])
@app.route('/degreeworks/<id>')
def degreeworks(id):
    cur=mysql.connection.cursor()
    flag=cur.execute("select * from CourseStudent where studentID= '"+id+"' ")
    degreeworkinfo=cur.fetchall()
    cur.close()
    if flag==0:
        return "<strong> You did not take any previous courses</strong>"
    else:
        return render_template("degreeworks.html", degreeworkinfo=degreeworkinfo)


@app.route('/works/<id>',methods=['GET', 'POST'])
def works(id):
    if request.method=='POST':
        choice=request.form
        finalchoice=choice["choice"]
        if int(finalchoice)==1:
            return redirect(url_for('viewAvailableCourses',id=id))
        elif int(finalchoice)==2:
            return redirect(url_for('specificCourse',id=id))

        else:
            return "Please choose Number between 1-2 Representing your Choice"
    return render_template("works.html")

@app.route('/SpecificCourse/<id>', methods=['GET','POST'])
def specificCourse(id):
    if request.method=='POST':
        specificone = request.form
        deptCode = specificone['deptCode']
        courseNum = specificone['CourseNumber']
        if deptCode == '':
            return "deptCode field is Empty"
        if courseNum == '':
            return "courseNum field is Empty"
        cur = mysql.connection.cursor()
        flag = cur.execute(" select * from Course where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        courseinfo=cur.fetchall()
        if flag == 0:
            return "Course does not exist"

        flag2 = cur.execute("select * from CoursePrereq where deptCode='" + deptCode + "' and courseNum='" + courseNum + "' ")
        allprereq = cur.fetchall()
        print("This is the prereq", allprereq)
        avcourselist=[]
        avcourselist.extend([courseinfo])
        takenflag = cur.execute("select * from CourseStudent where deptCode='" + deptCode + "' and courseNum='" + courseNum + "' and studentID='" + id + "' and letterGrade!='F' ")
        if takenflag == 0:
            if flag2 == 0:
                return render_template("cantake.html",courseinfo=courseinfo,courseprereq=allprereq)
            else:
                finalflag = True

                for prereq in allprereq:
                    prereqNum = str(prereq[3])
                    flag3 = cur.execute("select * from CourseStudent where deptCode='" + prereq[2] + "' and courseNum='" + prereqNum + "' and studentID='" + id + "' and letterGrade!='F' ")
                    if flag3 == 0 and prereq[2] != "SPAM":
                        finalflag = False

                if finalflag == True:
                    return render_template("cantake.html",courseinfo=courseinfo,courseprereq=allprereq)
                else:
                    return render_template("Can'ttake.html", courseinfo=courseinfo, courseprereq=allprereq)
        else:
            return "<strong>You have already Passed this course</strong>"
        cur.close()
    return render_template("specificCourse.html")



@app.route('/viewreviews', methods=['GET','POST'])
def viewReviews():
    if request.method=="POST":
        coursereview=request.form
        deptCode=coursereview['deptCode']
        courseNum=coursereview['CourseNumber']
        if deptCode=='':
            return "deptCode field is Empty"
        if courseNum=='':
            return "courseNum field is Empty"
        cur = mysql.connection.cursor()
        flag = cur.execute(" select * from Course where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        if flag == 0:
            return "Course does not exist"

        flag=cur.execute("select * from Reviews where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        reviews=cur.fetchall()
        if flag==0:
            return "There are no Reviews Available at the moment for the course chosen"
        cur.close()
        return render_template("viewreviewtable.html", reviewdetails=reviews)

    return render_template("ViewReviews.html")

@app.route('/postreviews/<id>', methods=['GET','POST'])
def postReviews(id):
    if request.method == "POST":
        coursereview = request.form
        deptCode = coursereview['deptCode']
        courseNum = coursereview['CourseNumber']
        rating=coursereview['rating']
        textualreview=coursereview['textualreview']
        if deptCode == '':
            return "deptCode field is Empty"
        if courseNum == '':
            return "courseNum field is Empty"
        if rating == '':
            return "rating field is Empty"
        if textualreview == '':
            return "textualreview field is Empty"

        cur = mysql.connection.cursor()
        flag = cur.execute(" select * from Course where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        if flag == 0:
            return "Course does not exist"

        flag = cur.execute("select * from CourseStudent where deptCode='" + deptCode + "' and courseNum='" + courseNum + "' and StudentID='"+id+"'")
        if flag==0:
            verified="N"
        else:
            verified="Y"
        if ((int(rating)<1) or (int(rating)>5)):
            return "Invalid Rating Please Enter a number from 1-5"
        reviewdate=date.today()
        cur.execute("INSERT INTO Reviews values (%s,%s,%s,%s,%s,%s,%s)",(id,deptCode,courseNum,rating,textualreview,verified,reviewdate))
        cur.connection.commit()
        cur.close()
        return "Review Added successfully"
    return render_template("PostReviews.html")

@app.route('/viewcourseinfo', methods=['GET','POST'])
def viewCourseInfo():
    if request.method == "POST":
        courseinfo = request.form
        deptCode = courseinfo['deptCode']
        courseNum = courseinfo['CourseNumber']
        if deptCode == '':
            return "deptCode field is Empty"
        if courseNum == '':
            return "courseNum field is Empty"
        cur = mysql.connection.cursor()
        flag = cur.execute(" select * from Course where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        if flag == 0:
            return "Course does not exist"
        courseinfoinit=cur.execute("select * from Course where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        courseinfo=cur.fetchall()
        courseprereqinit=cur.execute("select * from CoursePrereq where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        courseprereq=cur.fetchall()
        coursecrosslistedinit = cur.execute("select * from CourseCrosslisted where deptCode='" + deptCode + "' and courseNum='" + courseNum + "'")
        coursecrosslisted=cur.fetchall()
        cur.close()
        return render_template("courseinfotable.html",courseinfo=courseinfo,courseprereq=courseprereq,coursecrosslisted=coursecrosslisted)
    return render_template("ViewCourseInfo.html")

@app.route('/viewavailablecourses/<id>', methods=['GET','POST'])
def viewAvailableCourses(id):
    if request.method == "POST":
        #return "Method is post"
        response=request.form
        semester=response['semester']
        count = 0
        semesterlist = ['Fall', 'Spring', 'Winter', 'Summer','fall', 'spring', 'winter', 'summer','n']
        for item in semesterlist:
            if (semester != item):
                count = count + 1
            else:
                break
        if (count == 9):
            return "Semester is not Valid, Make sure you type it in in the right way"
        cur=mysql.connection.cursor()
        flag=cur.execute("select deptCode from StudentDepartment where studentID='"+id+"'")
        deptcodeinit=cur.fetchall()
        if flag!=0:
            deptCode=deptcodeinit[0][0]
        if semester=="Fall" or semester=="fall":
            flag = cur.execute("select * from Course where deptCode='" + deptCode + "' and semester LIKE '%fall%' or '%Fall%' or semester= 'N/A' ")
        elif semester == "Spring" or semester == "spring":
            flag = cur.execute("select * from Course where deptCode='" + deptCode + "' and semester LIKE '%spring%' or '%Spring%' or semester= 'N/A' ")
        elif semester == "Winter" or semester == "winter":
            flag = cur.execute("select * from Course where deptCode='" + deptCode + "' and semester LIKE '%Winter%' or '%winter%' or semester= 'N/A' ")
        elif semester == "Summer" or semester == "summer":
            flag = cur.execute("select * from Course where deptCode='" + deptCode + "' and semester LIKE '%Summer%' or '%summer%' or semester= 'N/A' ")
        elif semester=="n":
            flag = cur.execute("select * from Course where deptCode='" + deptCode + "'")
        avcourselist=[]
        if flag!=0:
            coursetuple=cur.fetchall()
            print (coursetuple)
            for course in coursetuple:
                deptCodenew=course[0]
                courseNumnew=str(course[1])
                flag2=cur.execute("select * from CoursePrereq where deptCode='" + deptCodenew + "' and courseNum='" + courseNumnew + "' ")
                allprereq=cur.fetchall()
                print ("This is the prereq",allprereq)
                takenflag=cur.execute("select * from CourseStudent where deptCode='" + deptCodenew + "' and courseNum='" +courseNumnew + "' and studentID='"+id+"' ")
                if takenflag==0:
                    if flag2==0:
                        avcourselist.extend([course])
                    else:
                        finalflag=True

                        for prereq in allprereq:
                            prereqNum=str(prereq[3])
                            flag3=cur.execute("select * from CourseStudent where deptCode='" + prereq[2] + "' and courseNum='" +prereqNum + "' and studentID='"+id+"' and letterGrade!='F' ")
                            if flag3==0 and prereq[2]!="SPAM":
                                finalflag=False

                        if finalflag==True:
                            avcourselist.extend([course])
        cur.close()
        return render_template("availablecoursestable.html", courseinfo=avcourselist)
    # else:
    #     return "Method is not POst"




    return render_template("ViewAvailableCourses.html")





# @app.route('/users')
# def users():
#     cur = mysql.connection.cursor()
#     result=cur.execute("select * from users")
#     details=cur.fetchall()
#     if details is None:
#         return "Failed to find any instances"
#     cur.close()
#     return render_template("user.html", userdetails=details)




if __name__=="__main__":
    app.run(debug=True)
