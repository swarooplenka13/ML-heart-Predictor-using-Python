from datetime import datetime as dt
from email import message
from time import time
from flask import Flask,flash, make_response, redirect, session, url_for, request,render_template
from fpdf import FPDF
from predict import calc
import bcrypt
import pymongo
app = Flask(__name__)
app.secret_key = "supersecretkey"
# app.config["MONGO_URI"] = "mongodb+srv://swaroop:Es5BLdcibccqkAAC@cluster0.8awsvf9.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient("mongodb+srv://swaroop:Es5BLdcibccqkAAC@cluster0.8awsvf9.mongodb.net/?retryWrites=true&w=majority")
db = client.get_database('ml')
records = db.register
@app.route('/')
def home():
    return render_template('index.html',message="")

@app.route('/predictheartdisease',methods = ['POST','GET'])
def index():
    res=""
    if(request.method=='POST'):
          # age	sex	cp	trestbps	chol	fbs	restecg	thalach	exang	oldpeak	slope	ca	thal 
         age = request.form.get('age')
         sex = request.form.get('sex')
         cp = request.form.get('cp')
         trestbps = request.form.get('trestbps')
         chol = request.form.get('chol')
         fbs = request.form.get('fbs')
         restecg = request.form.get('restecg')
         thalach = request.form.get('thalach')
         exang = request.form.get('exang')
         oldpeak=  request.form.get('oldpeak')
         slope = request.form.get('slope')
         ca=  request.form.get('ca')
         thal= request.form.get('thal')
         now = dt.now()
         s=dt.isoformat(now)
         x = calc((int(age),int(sex),int(cp),int(trestbps),int(chol),int(fbs),int(restecg),int(thalach),int(exang),float(oldpeak),int(slope),int(ca),int(thal)))
         if x==0:
                res="You may not have any heart disease,But maintain good health :)"
         else:
                res="You have the heart disease ,maintain good health!!"
         records.update_one({"email":session['email']},{
            "$push":{
                    "data":{
                        "age":age,
                        "sex":sex,
                        "cp":cp,
                        "trestbps":trestbps,
                        "chol":chol,
                        "fbs" : fbs,
                        "restecg" : restecg,
                        "thalach" : thalach,
                        "exang" : exang,
                        "oldpeak":  oldpeak,
                        "slope" : slope,
                        "ca": ca,
                        "thal": thal,
                        "date":s,
                        "res":res
                    },   
            },
        })
        #  records.delete_one({"email":session['email']})
         return render_template('predict.html',res=res)
        
    return render_template('predict.html',res="")

@app.route('/register',methods = ['POST','GET'])
def reg():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("Phone")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html',message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html',message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html',message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed,'phone':phone}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
   
            return redirect(url_for('login'))

    return render_template('register.html') 
@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

       
        email_found = records.find_one({"email": email})
        print(email_found)
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session["name"]= email_found['name']
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        name=session["name"]
        return render_template('dashboard.html', email=email,name=name)
    else:
        return redirect(url_for("login"))       


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("login.html")
    else:
        return render_template('index.html',message="")

@app.route("/download")
def hell():
        feed=records.find_one({"email": session['email']}) 
        feed1=feed['data']
        print(feed)  
        pdf = FPDF()
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin	
        pdf.set_font('Times','B',14.0) 
        pdf.cell(page_width, 0.0, 'Diagnosis Report', align='C')
        pdf.ln(10)
        pdf.cell(page_width, 0.0, '- Contact Information -', align='C')
        pdf.set_font('Times','',12.0) 
        col_width = page_width/6
        pdf.ln(1)
        th = pdf.font_size
        pdf.cell(col_width, th, "Name: ",align="L")
        pdf.cell(col_width, th, feed['name'],align="R")
        pdf.ln(th)
        pdf.cell(col_width, th, "Email: ",align="L")
        pdf.cell(col_width, th, feed['email'],align="R")
        pdf.ln(th)
        pdf.cell(col_width, th,"Phone Number: ",align="L")
        pdf.cell(col_width, th, feed['phone'],align="R") 
        pdf.ln(th)
        pdf.cell(page_width, 0.0, '- end -', align='C')  
        pdf.ln(th)
        pdf.ln(1)
        pdf.ln(2)
        i=1
        for row in feed1:
             pdf.ln(th)
             pdf.ln(th) 
             pdf.cell(page_width, 0.0,str(i)+". Report", align='C') 
             pdf.ln(th)            
             pdf.cell(col_width, th, "Date&Time: ",align="L")
             pdf.ln(th)
             pdf.cell(col_width, th, row['date'],align="L")
             pdf.ln(th)
             pdf.cell(col_width, th, "Age: ",align='L')
             pdf.cell(col_width, th, row['age'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "Gender: ")
             if row['sex']==0:
                  pdf.cell(col_width, th,"Female",align='R')
                  pdf.ln(th)
             else:
                  pdf.cell(col_width, th,"Male",align='R')
                  pdf.ln(th)
             pdf.cell(col_width, th, "Chest pain: ",align='L')
             pdf.cell(col_width, th, row['cp'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, " Resting blood pressure:",align='L')
             pdf.cell(col_width, th, row['trestbps'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "Serum cholestoral in mg/dl: ",align='L')
             pdf.cell(col_width, th, row['chol'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "Fasting blood sugar: ",align='L')
             pdf.cell(col_width, th, row['fbs'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "Resting ecg results: ",align='L')
             pdf.cell(col_width, th, row['restecg'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "Maximum heart rate: ",align='L')
             pdf.cell(col_width, th, row['thalach'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "Exercise included angina: ",align='L')
             pdf.cell(col_width, th, row['exang'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "ST depression induced by exercise relative to rest: ",align='L')
             pdf.ln(th)
             pdf.cell(col_width, th, row['oldpeak'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "The slope of peak ST segment: ",align='L')
             pdf.cell(col_width, th, row['slope'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "The No. of major vessels colored by flourosopy: ",align='L')
             pdf.ln(th)
             pdf.cell(col_width, th, row['ca'],align='R')
             pdf.ln(th)
             pdf.cell(col_width, th, "Thal(0 = normal ; 1 = fixeed defect ; 2 = reversible defect): ",align='L')
             pdf.ln(th)
             pdf.cell(col_width, th, row['thal'],align='R')
             pdf.ln(th)
             pdf.cell(col_width,th,"Result: ",align="L")
             pdf.ln(th)
             pdf.cell(col_width,th,row['res'],align="R")
             pdf.ln(th)
             pdf.ln(th)
             i+=1
             pdf.cell(page_width, 0.0, '- end of report -', align='C')
             pdf.ln(th)  
        pdf.ln(2)
        pdf.ln(th)	
        pdf.set_font('Courier', '', 12)	    
        pdf.ln(th)	
        pdf.ln(10)	
        pdf.set_font('Times','',10.0) 
        pdf.cell(page_width, 0.0, '- © ML heart predictor -', align='C')    
        response = make_response(pdf.output(dest='S').encode('latin-1'))
        response.headers.set('Content-Disposition', 'attachment;filename= Diagnosis.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response            



if __name__ == '__main__':
   app.run(debug = True,port="5500")