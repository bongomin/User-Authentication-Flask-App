import os
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb.cursors import DictCursor 
from functools import wraps
# from werkzeug.utils import secure_filename

from data import Articles


app =Flask(__name__)
# setup mysql
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='danny'
app.config['MYSQL_DB']='myapp'
app.config['MYSQL_PASSWORD']='P@55w0rd55'

# initialising msysl
mysql=MySQL(app)

Articles =Articles()



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/articles')
def articles():
    return render_template('articles.html',articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html',id=id)


class RegisterForm(Form):
    name = StringField('Your Full Name',[validators.Length(min=1,max=50)])
    username = StringField('Username',[validators.length(min=4,max=25)])
    email= StringField('Email',[validators.length(min=6,max=50)])
    password = PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm',message='password do not match')])
    confirm =  PasswordField('confirm password')

# user  Registration
@app.route('/register',methods=['GET','POST'])
def register():    
    form = RegisterForm(request.form)
    if request.method ==  'POST' and form.validate():
       name = form.name.data
       email = form.email.data
       username = form.username.data
       password = sha256_crypt.encrypt(str(form.password.data))


      #  creating the cursor
       cur = mysql.connection.cursor()

      # excecute query
       cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)", (name,email,username,password))

      #  commit to db
       mysql.connection.commit()
      #  close connection
       cur.close()

       flash('you are now registered and you can login to the system','success')


       redirect(url_for('home')) 
    return render_template('register.html', form=form)  


#user login   
@app.route('/login',methods=['GET','POST'])
def login():
  if request.method == 'POST':
    #get form fileds
    username = request.form['username']
    password_candidate =request.form['password'] 

    #create cusor
    cur = mysql.connection.cursor(DictCursor)

    #get user by user name
    result = cur.execute("SELECT * FROM users WHERE username = %s",[username])

    if result > 0:
       data = cur.fetchone()
       password = data['password']

       #compare passwords
       if sha256_crypt.verify(password_candidate,password):
           session['logged_in'] = True
           session['username'] = username


           flash('you are logged in ','success')
           return redirect(url_for('home'))
       else:
           error ='invalid login'
           return render_template('login.html',error = error)
    else:
        error ='username not found'
        return render_template('login.html',error = error )

    cur.close()

  return render_template('login.html') 

  # check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if'logged_in' in session:
           return f(*args,**kwargs)
        else:
          flash('unauthorised please login first','danger')
          return redirect(url_for('login'))

    return wrap      

# logout
@app.route('/logout')
@is_logged_in
def logout():
  session.clear()
  flash('you are logged out of the system','success')
  return redirect(url_for('login'))



  return render_template('login.html') 








if __name__=='__main__':
    app.secret_key='gCUUNjVc9f'
    app.run(debug=True)