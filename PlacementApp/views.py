from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
import pickle
import pymysql
import os
from django.core.files.storage import FileSystemStorage
from datetime import date

# Using Django sessions for state management instead of global variables

def getCompany(job_id):
    company = ""
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select company_name from jobs where job_id='"+str(job_id)+"'")
        rows = cur.fetchall()
        for row in rows:
            company = row[0]
            break
    return company

def getScore(student_name):
    score = ""
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select score from profile where student_name='"+student_name+"'")
        rows = cur.fetchall()
        for row in rows:
            score = row[0]
            break
    return score

def ViewPerformance(request):
    if request.method == 'GET':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'CompanyLogin.html', {'data': 'Session expired. Please login again.'})
            
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Job ID</th><th><font size="3" color="black">Student Name</th>'
        output+='<th><font size="3" color="blue">Status</th><th><font size="3" color="blue">Exam Score</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM applyjob")
            rows = cur.fetchall()
            for row in rows:
                company = getCompany(row[0])
                score = getScore(row[1])
                if company == username:
                    output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td>'
                    output+='<td><font size="3" color="black">'+str(row[2])+'</td><td><font size="3" color="black">'+str(score)+'</td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'CompanyScreen.html', context)
    

def ViewFeedback(request):
    if request.method == 'GET':
        global uname
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Student name</th><th><font size="3" color="black">Challenges Feedback</th>'
        output+='</tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * from feedback")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'TPOScreen.html', context) 

def JobStatus(request):
    if request.method == 'GET':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'StudentLogin.html', {'data': 'Session expired. Please login again.'})
            
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Job ID</th><th><font size="3" color="black">Student Name</th>'
        output+='<th><font size="3" color="blue">Status</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM applyjob where student_name='"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="3" color="black">'+str(row[0])+'</td><td><font size="3" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="3" color="black">'+str(row[2])+'</td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'StudentScreen.html', context) 

def checkApplicationStatus(job_id, username):
    status = "none"
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select student_name FROM applyjob where job_id='"+job_id+"' and student_name='"+username+"'")
        rows = cur.fetchall()
        for row in rows:
            status = "already applied"
    return status

def runKNNML(skills, username):
    recommendation = []
    b = skills.split(",")
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM jobs")
        rows = cur.fetchall()
        for row in rows:
            job_id = str(row[0])
            status = checkApplicationStatus(job_id, username)
            if status == "none":
                company = row[1]
                desc = row[2]
                salary = row[3]
                job_post_date = row[4]
                last_date = row[5]
                required_skills = row[6]
                a = required_skills.split(",")
                knn_predict = len(set(a).intersection(b)) / float(len(set(a)))
                print(str(a)+" === "+str(b)+" === "+str(knn_predict))
                if knn_predict > 0:
                    recommendation.append([job_id, company, desc, salary, job_post_date,last_date,required_skills,knn_predict])
    recommendation.sort(key = lambda x : x[7], reverse=True)
    return recommendation

def ExamTestAction(request):
    if request.method == 'POST':
        job_id = request.POST.get('job', False)
        total = 0
        
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'StudentLogin.html', {'data': 'Session expired. Please login again.'})
        
        # Get correct answers from session
        correct_answers = request.session.get('correct_answers', [])
        num_questions = request.session.get('num_questions', 0)
        
        for i in range(len(correct_answers)):
            user_answer = request.POST.get("t"+str(i+1), False)
            correct_answer = correct_answers[i]
            print(user_answer+" "+correct_answer)
            if correct_answer == user_answer:
                total += 1
        
        if total > 0 and len(correct_answers) > 0:
            total = total / len(correct_answers)
        if total > 0.80:
            status = "Selected"
        else:
            status = "Rejected"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update profile set score='"+str(total)+"' where student_name='"+username+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        # Reuse the same connection
        student_sql_query = "insert into applyjob value('"+job_id+"','"+username+"','"+status+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        
        context= {'data':'<font size=3 color=blue>Your total marks = '+str(total)+'</font>'}
        return render(request, 'StudentScreen.html', context)          

def ApplyJob(request):
    if request.method == 'GET':
        job_id = request.GET.get('id', False)
        output = '<tr><td><font size="3" color="black">Job&nbsp;ID<input name="job" type="text" size="15" value="'+job_id+'"></td></td></tr>'
        correct_answers = []
        i = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM questions")
            rows = cur.fetchall()
            for row in rows:
                question = row[0]
                a = row[1]
                b = row[2]
                c = row[3]
                d = row[4]
                answer = row[5]
                output += '<tr><td><font size="4" color="black">Question = '+question+'</font></td></tr>'
                output += '<tr><td><font size="3" color="black">'+a+'</font><input type="radio" name="t'+str(i+1)+'" value="A"/></td></tr>'
                output += '<tr><td><font size="3" color="black">'+b+'</font><input type="radio" name="t'+str(i+1)+'" value="B"/></td></tr>'
                output += '<tr><td><font size="3" color="black">'+c+'</font><input type="radio" name="t'+str(i+1)+'" value="C"/></td></tr>'
                output += '<tr><td><font size="3" color="black">'+d+'</font><input type="radio" name="t'+str(i+1)+'" value="D"/></td></tr>'
                correct_answers.append(answer)
                i+=1
                output += '<tr><td></td></tr><tr><td></td></tr>'
        
        # Store correct answers in session
        request.session['correct_answers'] = correct_answers
        request.session['num_questions'] = i
        
        context= {'data1':output}
        return render(request, 'ExamTest.html', context)   

def Recommendation(request):
    if request.method == 'GET':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'StudentLogin.html', {'data': 'Session expired. Please login again.'})
            
        skills = ""
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select skills FROM profile where student_name='"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                skills = row[0]
                break
        recommendation = runKNNML(skills, username)
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="3" color="black">Job ID</th>'
        output+='<th><font size="3" color="black">Company Name</th><th><font size="3" color="black">Job Description</th>'
        output+='<th><font size="3" color="black">Salary</th><th><font size="3" color="black">Job Posted date</th>'
        output+='<th><font size="3" color="black">Last Applicant Date</th><th><font size="3" color="black">Required Skills</th>'
        output+='<th><font size="3" color="black">KNN Recommendation Probability</th><th><font size="3" color="blue">Apply Job</th>'
        output+='</tr>'
        for i in range(len(recommendation)):
            recommend = recommendation[i]
            output+='<tr><td><font size="3" color="black">'+recommend[0]+'</td><td><font size="3" color="black">'+str(recommend[1])+'</td>'
            output+='<td><font size="3" color="black">'+recommend[2]+'</td><td><font size="3" color="black">'+str(recommend[3])+'</td>'
            output+='<td><font size="3" color="black">'+recommend[4]+'</td><td><font size="3" color="black">'+str(recommend[5])+'</td>'
            output+='<td><font size="3" color="black">'+recommend[6]+'</td><td><font size="3" color="black">'+str(recommend[7])+'</td>'
            output +='<td><a href=\'ApplyJob?id='+recommend[0]+'\'><font size=3 color=red>Click Here to Apply</font></a></td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'StudentScreen.html', context)       

def Feedback(request):
    if request.method == 'GET':
       return render(request, 'Feedback.html', {})

def FeedbackAction(request):
    if request.method == 'POST':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'StudentLogin.html', {'data': 'Session expired. Please login again.'})
            
        feedback = request.POST.get('t1', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO feedback VALUES('"+username+"','"+feedback+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        status = "<font size=3 color=blue>Your feedback accepted successfully</font>"
        context= {'data': status}
        return render(request, 'Feedback.html', context)      

def AddQuestion(request):
    if request.method == 'GET':
       return render(request, 'AddQuestion.html', {})  

def PostJob(request):
    if request.method == 'GET':
       return render(request, 'PostJob.html', {})    

def CompanyLogin(request):
    if request.method == 'GET':
       return render(request, 'CompanyLogin.html', {})    

def TPOLogin(request):
    if request.method == 'GET':
       return render(request, 'TPOLogin.html', {})

def StudentLogin(request):
    if request.method == 'GET':
       return render(request, 'StudentLogin.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})    

def index(request):
    if request.method == 'GET':
        return render(request, 'index.html', {})   

def TPOLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register where username='"+username+"' and password='"+password+"' and usertype='TPO'")
            rows = cur.fetchall()
            for row in rows:
                utype = row[0]
                index = 1
                break		
        if index == 1:
            # Store username in session
            request.session['username'] = username
            context= {'data':'<font size=3 color=blue>Welcome '+username+"</font>"}
            return render(request, 'TPOScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'TPOLogin.html', context)        
    
def CompanyLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register where username='"+username+"' and password='"+password+"' and usertype='Company'")
            rows = cur.fetchall()
            for row in rows:
                utype = row[0]
                index = 1
                break		
        if index == 1:
            # Store username in session
            request.session['username'] = username
            context= {'data':'<font size=3 color=blue>Welcome '+username+"</font>"}
            return render(request, 'CompanyScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'CompanyLogin.html', context)

def StudentLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register where username='"+username+"' and password='"+password+"' and usertype='Student'")
            rows = cur.fetchall()
            for row in rows:
                utype = row[0]
                index = 1
                break		
        if index == 1:
            # Store username in session
            request.session['username'] = username
            context= {'data':'<font size=3 color=blue>Welcome '+username+"</font>"}
            return render(request, 'StudentScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'StudentLogin.html', context)          


def RegisterAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5')
        utype = request.POST.get('t6', False)
        
        status = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select username FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    status = username+" username already exists"
                    break
        if status == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"','"+utype+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            if db_cursor.rowcount == 1:
                status = "<font size=3 color=blue>Signup process successfully completed</font>"
            else:
                status = "error in signup"      
        else:
            status = "error in signup"        
        context= {'data': status}
        return render(request, 'Register.html', context)

def AddQuestionAction(request):
    if request.method == 'POST':
        global uname
        question = request.POST.get('t1', False)
        a = request.POST.get('t2', False)
        b = request.POST.get('t3', False)
        c = request.POST.get('t4', False)
        d = request.POST.get('t5', False)
        answer = request.POST.get('t6', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO questions VALUES('"+question+"','"+a+"','"+b+"','"+c+"','"+d+"','"+answer+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        status = "<font size=3 color=blue>Question details added successfully</font>"
        context= {'data': status}
        return render(request, 'AddQuestion.html', context)    

def PostJobAction(request):
    if request.method == 'POST':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'CompanyLogin.html', {'data': 'Session expired. Please login again.'})
            
        description = request.POST.get('t1', False)
        salary = request.POST.get('t2', False)
        apply_date = request.POST.get('t3', False)
        skills = request.POST.getlist('t4')
        skills = ','.join(skills)
        status = "error in adding job details"
        job_id = ""
        post_date = str(date.today()) 
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select max(job_id) FROM jobs")
            rows = cur.fetchall()
            for row in rows:
                job_id = row[0]
                break
        if job_id is not None:
            job_id = str(job_id + 1)
        else:
            job_id = "1"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO jobs VALUES('"+job_id+"','"+username+"','"+description+"','"+salary+"','"+post_date+"','"+apply_date+"','"+skills+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        status = "<font size=3 color=blue>Job details added successfully with JOB ID = "+job_id+"</font>"
        context= {'data': status}
        return render(request, 'PostJob.html', context)

def UpdateProfile(request):
    if request.method == 'GET':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'StudentLogin.html', {'data': 'Session expired. Please login again.'})
            
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select student_name FROM profile where student_name='"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                index = 1
                break
        if index == 0:
            return render(request, 'UpdateProfile.html', {})   
        else:
            return render(request, 'ModifyProfile.html', {})   

def UpdateProfileAction(request):
    if request.method == 'POST':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'StudentLogin.html', {'data': 'Session expired. Please login again.'})
            
        qualification = request.POST.get('t1', False)
        percentage = request.POST.get('t2', False)
        passout = request.POST.get('t3', False)
        experience = request.POST.get('t4', False)
        myfile = request.FILES['t5'].read()
        fname = request.FILES['t5'].name
        skills = request.POST.getlist('t6')
        skills = ','.join(skills)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO profile VALUES('"+username+"','"+qualification+"','"+percentage+"','"+passout+"','"+experience+"','"+fname+"','"+skills+"','0')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        if os.path.exists("PlacementApp/static/resumes/"+fname):
            os.remove("PlacementApp/static/resumes/"+fname)
        with open("PlacementApp/static/resumes/"+fname, "wb") as file:
            file.write(myfile)
        file.close()    
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = "<font size=3 color=blue>Profile successfully Updated</font>"
        else:
            status = "<font size=3 color=blue>error in updating profile</font>"        
        context= {'data': status}
        return render(request, 'StudentScreen.html', context)

def ModifyProfileAction(request):
    if request.method == 'POST':
        # Get username from session
        username = request.session.get('username', '')
        if not username:
            return render(request, 'StudentLogin.html', {'data': 'Session expired. Please login again.'})
            
        experience = request.POST.get('t1', False)
        myfile = request.FILES['t2'].read()
        fname = request.FILES['t2'].name
        skills = request.POST.getlist('t3')
        skills = ','.join(skills)
        
        # Save the resume file
        if os.path.exists("PlacementApp/static/resumes/"+fname):
            os.remove("PlacementApp/static/resumes/"+fname)
        with open("PlacementApp/static/resumes/"+fname, "wb") as file:
            file.write(myfile)
        file.close()
            
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'placement',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update profile set experience='"+experience+"', resume='"+fname+"', skills='"+skills+"' where student_name='"+username+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        status = "<font size=3 color=blue>Profile successfully updated</font>"
        context= {'data': status}
        return render(request, 'StudentScreen.html', context)
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
#from openai import OpenAI

def chatbot(request):
    return render(request, 'chatbot.html', {})
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Load JSON once
with open("chatbot_data.json", "r") as f:
    chatbot_data = json.load(f)

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def chatbot_api(request):
    user_msg = request.POST.get("msg").lower()
    user_words = set(user_msg.split())

    best_match = ""
    max_score = 0

    for item in chatbot_data:
        question_words = set(item["question"].split())

        # count matching words
        score = len(user_words & question_words)

        if score > max_score:
            max_score = score
            best_match = item["answer"]

    if max_score > 0:
        reply = best_match
    else:
        reply = "Sorry, I don't understand."

    return JsonResponse({"reply": reply})
def ViewPlacementCompanyWise(request):
    if request.method == 'GET':
        # Check session (TPO login)
        username = request.session.get('username', '')
        if not username:
            return render(request, 'TPOLogin.html', {'data': 'Session expired. Please login again.'})

        output = ''
        output += '<table border=1 align=center width=100%>'
        output += '<tr>'
        output += '<th><font size="3" color="black">Company Name</th>'
        output += '<th><font size="3" color="black">Job ID</th>'
        output += '<th><font size="3" color="black">Student Name</th>'
        output += '<th><font size="3" color="black">Status</th>'
        output += '<th><font size="3" color="black">Score</th>'
        output += '</tr>'

        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='placement', charset='utf8')
        with con:
            cur = con.cursor()

            # Join applyjob + jobs + profile
            query = """
            SELECT j.company_name, a.job_id, a.student_name, a.status, p.score
            FROM applyjob a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN profile p ON a.student_name = p.student_name
            ORDER BY j.company_name
            """
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                output += '<tr>'
                output += '<td>' + str(row[0]) + '</td>'
                output += '<td>' + str(row[1]) + '</td>'
                output += '<td>' + str(row[2]) + '</td>'
                output += '<td>' + str(row[3]) + '</td>'
                output += '<td>' + str(row[4]) + '</td>'
                output += '</tr>'

        output += "</table><br><br><br>"

        return render(request, 'TPOScreen.html', {'data': output})
def FutureDrivesAnnouncement(request):
    if request.method == 'GET':
        username = request.session.get('username', '')
        if not username:
            return render(request, 'TPOLogin.html', {'data': 'Session expired. Please login again.'})

        message = """
        <div style='text-align:center; margin-top:50px;'>
            <h2 style='color:green;'>🚀 Future Placement Drives</h2>
            <h3 style='color:blue;'>Upcoming Soon...</h3>
        </div>
        """

        return render(request, 'FutureDrives.html', {'data': message})