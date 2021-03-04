
from flask import Flask,render_template,request,redirect,url_for, flash, send_file,session
from flask_mysqldb import MySQL
import re

from werkzeug.exceptions import HTTPException

import datetime


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ONLINE_EXAMINATION_MANAGEMENT'
with app.app_context():
    mysql = MySQL(app)
    conn=mysql.connect
cursor=conn.cursor()

examid=1;
qnid=1;

def convert_to_list(t):
    return list(map(convert_to_list, t)) if isinstance(t, (list, tuple)) else t


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

app.secret_key = "secretkey"
@app.route('/',methods=['GET','POST'])
def index():
    return  render_template('mainpage.html')
@app.route('/admin',methods =['GET', 'POST'])
def main():
    msg = ''
    
    if request.method == 'POST':
        emailid = request.form['inputEmail']
        print(emailid)
        password = request.form['inputPassword']

        cursor.execute('SELECT * FROM ADMIN WHERE admin_email = %s AND admin_password = %s', (emailid, password,))
        account = cursor.fetchone()
        
        print(account)
        if account:
            session['user']=emailid
            session['loggedin'] = True
            msg = 'Logged in successfully !'

            return render_template('dashboard.html',msg=msg)
        else:
            flash('Incorrect username / password !')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html')
    else:
        flash('Login first!')
        return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('index'))

@app.route('/setquestions',methods =['GET', 'POST'])
def setquestions():
    if 'loggedin' in session:
        cursor.execute("SELECT * FROM ADMIN WHERE admin_email=%s",(session['user'],))
        adminid=cursor.fetchone()[0]
        print(adminid)
        if request.method == "POST":
            examtitle = request.form['examtitle']
            examdateandtime=request.form['examdateandtime']
            examenddateandtime=request.form['examenddateandtime']
            examduration=request.form['examduration']
            totalqns=request.form['totalqns']
            marksforcrt=request.form['markscrt']
            marksforwrg=request.form['markswrg']
            totalmarks=request.form['totalmarks']

            d=cursor.execute("SELECT * FROM ONLINE_EXAM")
            examid=d+1
            print("examid"+str(examid))
            cursor.execute("INSERT INTO ONLINE_EXAM(exam_title,admin_id,exam_datetime,exam_duration,total_questions,marks_for_correct,marks_for_wrong,total_marks,exam_end_datetime) VALUES (%s,%s,%s,%s,%s,%s, %s, %s,%s)", (examtitle,int(adminid),examdateandtime,examduration,int(totalqns),int(marksforcrt),int(marksforwrg),int(totalmarks),examenddateandtime,))

            
            conn.commit()
            cursor.execute("SELECT exam_id FROM ONLINE_EXAM ORDER BY  exam_id DESC LIMIT 1")

            session['exam_id']=cursor.fetchone()[0]
            return redirect(url_for('questions'))

        return render_template("setqns.html")
    else:
        flash('Login first!')
        return redirect(url_for('main'))
@app.route('/display_exam',methods=['GET','POST'])
def display_exam():

    if 'loggedin' in session:
        cursor.execute("SELECT * FROM ADMIN WHERE admin_email=%s",(session['user'],))
        adminid=cursor.fetchone()[0];
        cursor.execute("SELECT * FROM ONLINE_EXAM WHERE admin_id=%s",(adminid,))
        results=cursor.fetchall()
        return  render_template("display_exam.html",value=results)
    else:

        return redirect(url_for('main'))

@app.route('/fetchresults',methods =['GET', 'POST'])
def fetchresults():
    if 'loggedin' in session:
        if request.method =='GET':
            return render_template("fetchresults.html")
        if request.method == 'POST':
            examname=request.form["mquery"]
            cursor.execute("SELECT * FROM RESULTS AS R,STUDENT AS S, ONLINE_EXAM AS O WHERE R.student_id= S.student_id AND O.exam_id= R.exam_id AND O.exam_title=%s ORDER BY S.student_name",(examname,))
            results=cursor.fetchall();

            return  render_template("displayresults.html",results=results)
    else:
        flash('Login first!')
        return redirect(url_for('main'))

@app.route('/analysis',methods =['GET', 'POST'])
def analysis():
    if 'loggedin' in session:
        if request.method =='GET':
            cursor.execute("SELECT O.exam_title,COUNT(S.student_id),MAX(R.marks_obtained),MIN(R.marks_obtained),AVG(R.marks_obtained) FROM RESULTS AS R,STUDENT AS S, ONLINE_EXAM AS O WHERE R.student_id= S.student_id AND O.exam_id= R.exam_id GROUP BY (O.exam_id)")
            results=cursor.fetchall();
            return render_template("analysis.html",results=results)
        
    else:
        flash('Login first!')
        return redirect(url_for('main'))

@app.route('/questions',methods=['GET', 'POST'])
def questions():
    if 'loggedin' in session:
        if request.method == "GET":
            return render_template("questions.html")
        if request.method == "POST":
            question=request.form["ques"]
            a=request.form.get("a")
            b=request.form.get("b")
            c=request.form.get("c")
            d=request.form.get("d")
            answer =request.form.get("options")
            print(answer)
            
            x=cursor.execute("SELECT * FROM QUESTION")
            qnid=x+1
        

            cursor.execute("INSERT INTO QUESTION(question_id,exam_id,question_title) VALUES (%s,%s,%s)", ((x+1),session['exam_id'],question,))
            conn.commit()

            x=cursor.execute("SELECT * FROM QN_OPTION")

            cursor.execute("INSERT INTO QN_OPTION VALUES (%s,%s,%s,%s)", ((x+1),qnid,1,a))
            conn.commit()
            x=cursor.execute("SELECT * FROM QN_OPTION")

            cursor.execute("INSERT INTO QN_OPTION VALUES (%s,%s,%s,%s)", ((x+1),qnid,2,b))
            conn.commit()
            x=cursor.execute("SELECT * FROM QN_OPTION")

            cursor.execute("INSERT INTO QN_OPTION VALUES (%s,%s,%s,%s)", ((x+1),qnid,3,c))
            conn.commit()
            x=cursor.execute("SELECT * FROM QN_OPTION")

            cursor.execute("INSERT INTO QN_OPTION VALUES (%s,%s,%s,%s)", ((x+1),qnid,4,d))
            conn.commit()

            cursor.execute("SELECT * FROM QN_OPTION WHERE question_id=%s AND option_number=%s",(qnid,answer,))
            optionid=cursor.fetchone()[0];

            cursor.execute("UPDATE QUESTION SET answer_option_id= (%s) WHERE question_id=%s ", (optionid,qnid))
            conn.commit()
            return redirect(url_for('questions'))


        return render_template("questions.html")
    else:

        return redirect(url_for('main'))
@app.route('/displayquestions')
def displayquestions():
    if 'loggedin' in session:
        examid=session['exam_id']
        print(examid)
        cursor.execute("SELECT * FROM QUESTION AS Q ,ONLINE_EXAM AS O WHERE Q.exam_id=O.exam_id AND Q.exam_id = %s", (examid,))
        questions=cursor.fetchall()
        cursor.execute(" SELECT * FROM QN_OPTION AS O,QUESTION AS Q WHERE O.question_id= Q.question_id  AND Q.exam_id= %s",(examid,))
        options =cursor.fetchall()
        return render_template("displayquestions.html",questions=questions,options=options)
    else:
        return redirect(url_for('main'))

@app.route('/update/<examid>',methods=['GET','POST'])
def update(examid):

    if request.method=='GET':

        print(examid[1:-1])
        examid=examid[1:-1]
        session['examid']=examid
        cursor.execute("USE ONLINE_EXAMINATION_MANAGEMENT")
        cursor.execute("SELECT * FROM ONLINE_EXAM AS O WHERE O.exam_id = %s", (examid,))
        value=cursor.fetchone()


        return render_template("edit_exam_details.html",value=value)
    if request.method == 'POST':
        examid=examid[1:-1]
        examtitle = request.form['examtitle']
        examdateandtime=request.form['examdateandtime']
        examenddateandtime=request.form['examenddateandtime']
        examduration=request.form['examduration']

        cursor.execute("UPDATE ONLINE_EXAM SET exam_title= %s,exam_datetime=%s,exam_end_datetime=%s,exam_duration=%s WHERE exam_id=%s", (examtitle,examdateandtime,examenddateandtime,examduration,
                                                                                             examid,))
        conn.commit()
        msg="Updated!"
        return render_template("dashboard.html",msg=msg)




@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        emailid = request.form.get('inputEmail')

        password = request.form.get('inputPassword')

        cursor.execute('SELECT * FROM STUDENT WHERE student_email = %s AND student_password = %s', (emailid, password,))
        account = cursor.fetchall()

        print(account)
        if account:
            session['email']=emailid
            session['stu_id']=account[0][0]
            session['name']=account[0][1]
            session['address']=account[0][4]
            session['phno']=account[0][5]

            session['loggedin'] = True
            msg = 'Logged in successfully !'

            return render_template('student_dashboard.html',stu_id=session['stu_id'],name=session['name'],email=session['email'],address=session['address'],phno=session['phno'])
        else:
            flash('Incorrect username / password !')


    return render_template('login_student.html', msg = msg)

@app.route('/student_dashboard',methods =['GET', 'POST'])
def student_dashboard():
    if 'loggedin' in session:
        return render_template('student_dashboard.html',stu_id=session['stu_id'],name=session['name'],email=session['email'],address=session['address'],phno=session['phno'])
    else:
        flash('Login first!')
        return redirect(url_for('login'))

@app.route('/exam_schedule', methods =['GET', 'POST'])
def exam_schedule():
    if 'loggedin' in session:
        cursor.execute("SELECT * FROM ONLINE_EXAM;")
        results=cursor.fetchall();
        return  render_template("exam_schedule.html",value=results)
    else:

        return redirect(url_for('main'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        password = request.form['Password']
        emailid = request.form['EmailID']
        name=request.form['StudentName']
        id=request.form['StudentID']
        contact=request.form['ContactNumber']
        address=request.form['Address']
        gender=request.form['Gender']

        cursor.execute("SELECT * FROM ONLINE_EXAMINATION_MANAGEMENT.STUDENT WHERE student_id = % s", (id, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', emailid):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', id):
            msg = 'Username must contain only characters and numbers !'
        elif not id or not password or not emailid:
            msg = 'Please fill out the form !'
        else:
            cursor.execute("INSERT STUDENT VALUES (%s,%s,%s,%s, % s, % s, % s)", (id,name,emailid,password,address,contact,gender,))
            conn.commit()
            msg = 'You have successfully registered !'
            return redirect(url_for('index'))

    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('register_student.html', msg=msg)

@app.route('/updatestudent',methods=['GET','POST'])
def updatestudent():

    if request.method=='GET':

        cursor.execute("USE ONLINE_EXAMINATION_MANAGEMENT")
        cursor.execute("SELECT * FROM STUDENT AS S WHERE S.student_email = %s", (session['email'],))
        value=cursor.fetchone()


        return render_template("update_student.html",value=value)
    if request.method == 'POST':
        password = request.form['Password']
        session['emailid'] = request.form['EmailID']
        session['name']=request.form['StudentName']

        session['phno']=request.form['ContactNumber']
        session['address']=request.form['Address']



        cursor.execute("UPDATE STUDENT SET student_name= %s,student_email= %s,student_password= %s,student_contact_no= %s,student_address= %s WHERE student_id=%s", (session['name'],session['emailid'],password,session['phno'],session['address'],session['stu_id'],))
        conn.commit()
        msg="Updated!"
        return render_template('student_dashboard.html',stu_id=session['stu_id'],name=session['name'],email=session['email'],address=session['address'],phno=session['phno'])

@app.route('/displayresults',methods =['GET', 'POST'])
def displayresults():
    if 'loggedin' in session:
        student_email=session['email']

        d=cursor.execute("SELECT * FROM RESULTS AS R,STUDENT AS S, ONLINE_EXAM AS O WHERE R.student_id= S.student_id AND O.exam_id= R.exam_id AND S.student_email=%s",(student_email,))
        results=cursor.fetchall();
        print(results)
        return render_template("displayresultsstudent.html",results=results)

    else:
        flash('Login first!')
        return redirect(url_for('main'))

@app.route('/take_exam/<examid>',methods=['GET','POST'])
def take_exam(examid):

    if request.method=='GET':
        questions=[]
        options=[]
        print(examid[1:-1])
        examid=examid[1:-1]
        session['examid']=examid
        cursor.execute("USE ONLINE_EXAMINATION_MANAGEMENT")
        qnlength=cursor.execute("SELECT * FROM QUESTION AS Q,ONLINE_EXAM AS O WHERE Q.exam_id=O.exam_id AND Q.exam_id = %s", (examid,))
        questions=cursor.fetchall()

        cursor.execute(" SELECT * FROM QN_OPTION AS O,QUESTION AS Q WHERE O.question_id= Q.question_id  AND Q.exam_id= %s",(examid,))
        options =cursor.fetchall()
        session['attempted']="false"
        return render_template("take_exam.html",questions=questions,options=options)




@app.route('/results',methods=['GET','POST'])
def results():
    
        correct=0
        wrong=0
        examid=session['examid']
        print(examid)
        cursor.execute("SELECT E.marks_for_correct FROM ONLINE_EXAM AS E WHERE E.exam_id=%s",(examid,))
        marks_for_correct=cursor.fetchall()
        cursor.execute("SELECT E.marks_for_wrong FROM ONLINE_EXAM AS E WHERE E.exam_id=%s",(examid,))
        marks_for_wrong=cursor.fetchall()
        cursor.execute("SELECT E.total_marks FROM ONLINE_EXAM AS E WHERE E.exam_id=%s",(examid,))
        total_marks=cursor.fetchall()
        cursor.execute("SELECT E.exam_title FROM ONLINE_EXAM AS E WHERE E.exam_id=%s",(examid,))
        exam_title=cursor.fetchall()
        #print("marks for correct")
        marks_for_correct1=convert_to_list(marks_for_correct)[0][0]
        marks_for_wrong_1=convert_to_list(marks_for_wrong)[0][0]
        total_marks_1=convert_to_list(total_marks)[0][0]
        exam_title_1=convert_to_list(exam_title)[0][0]
        for i in request.form:
            optionid=request.form.get(i)
            #print(optionid)
            examid1=[]
            cursor.execute("SELECT Q.exam_id FROM QUESTION AS Q WHERE Q.question_id=%s",(i,))
            examid1=convert_to_list(cursor.fetchall())
            examid=[val for sublist in examid1 for val in sublist]
            #print(examid1)
            cursor.execute("SELECT DISTINCT Q.answer_option_id FROM QN_OPTION AS O,QUESTION AS Q WHERE Q.question_id=O.question_id AND Q.question_id=%s",(i,))
            correct_option=convert_to_list(cursor.fetchall())



            if int(optionid)==int(correct_option[0][0]):
                correct+=1
            else:
                wrong+=1
            cursor.execute("SELECT student_id FROM STUDENT WHERE student_email=%s",(session['email'],))
            stu_id=session.get('stu_id',None)
            j=cursor.execute("SELECT * FROM STUDENT_RESPONSE")
            j=j+1
            cursor.execute("INSERT INTO STUDENT_RESPONSE values (%s,%s,%s,%s,%s)",(j,stu_id,str(examid1[0][0]),i,optionid))
            
            conn.commit()



        result=correct*marks_for_correct1-wrong*marks_for_wrong_1
        cursor.execute("INSERT INTO RESULTS(student_id,exam_id,marks_obtained) values (%s,%s,%s)", (stu_id,examid1[0],result))

        conn.commit()
        return render_template('results.html',result=result,total=total_marks_1)


@app.route('/delete_exam/<examid>',methods=['GET','POST'])
def delete_exam(examid):
    if request.method=='GET':
        examid=examid[1:-1]
        cursor.execute("DELETE FROM ONLINE_EXAM WHERE exam_id=%s",(examid,))
        #cursor.execute("DELETE FROM ")
        conn.commit()
    cursor.execute("SELECT * FROM ADMIN WHERE admin_email=%s",(session['user'],))
    adminid=cursor.fetchone()[0];
    cursor.execute("SELECT * FROM ONLINE_EXAM WHERE admin_id=%s",(adminid,))
    results=cursor.fetchall()
    return  render_template("display_exam.html",value=results)


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("404.html", e=e), 500



if __name__ == '__main__':
    app.run(debug=True)