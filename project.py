from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, TextField, SubmitField, RadioField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_bootstrap import Bootstrap

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hin'
app.config['MYSQL_DB'] = 'product'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

# homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')
#Get Coupon
@app.route('/getcoupon')
def getcoupon():
    return render_template('getcoupon.html')
# About our company
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')
#Voting Form class
class VotingForm(Form):
      card = RadioField('card', choices = [('S','SM5 SUN'),('M','SM5 MOON')])
#User vote
@app.route('/voting', methods=['GET', 'POST'])
def voting():
    form3 = VotingForm(request.form)
    if request.method == 'POST' and form3.validate():
        card = form3.card.data
        # Create connection
        cur = mysql.connection.cursor()
        # Execute the SQL command
        cur.execute("INSERT INTO vote(card) VALUES( %s)", (card))
        # Commit the changes in DB
        mysql.connection.commit()
        cur.close()
        flash('You have been successfully  voted ', 'success')
        return redirect(url_for('voting'))
    return render_template('voting.html', form3=form3)
#Make order form Class
class MkorderForm(Form):
     phone = TextField("Phone",[validators.Required("Please enter your phonenumber."),validators.Length(min=8, max=8)])
     email = TextField("Email",[validators.Required("Please enter your email address."), validators.Email("Please enter your email address:example@domain.com")])
     submit = SubmitField("Send")
@app.route('/makeorder', methods=['GET', 'POST'])
#Consumer make order
def makeorder():
    form1 = MkorderForm(request.form)
    if request.method == 'POST' and form1.validate():
        phone = form1.phone.data
        email = form1.email.data
        # Create connection
        cur = mysql.connection.cursor()
        #Execute the SQL command
        cur.execute("INSERT INTO makeorder(phone, email) VALUES( %s, %s)", (phone, email))
        # Commit the changes in DB
        mysql.connection.commit()
        cur.close()
        flash('You are success to make order ', 'success')

        return redirect(url_for('makeorder'))
    return render_template('makeorder.html', form1=form1)
# SignupForm Class
class SignupForm(Form):
    username = TextField('Username', [validators.Length(min=3, max=15)])
    email = StringField('Email', [validators.Required("please enter your email address"), validators.Email("Please enter your email address:example@domain.com")])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Confirm password do not match password')
    ])
    confirm = PasswordField('Confirm Password')
# Consumer sign up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form2 = SignupForm(request.form)
    if request.method == 'POST' and form2.validate():
        username = form2.username.data
        email = form2.email.data
        password = sha256_crypt.encrypt(str(form2.password.data))
        # Create connection
        cur = mysql.connection.cursor()
        # Execute the SQL command
        cur.execute("INSERT INTO usr(username, email, password) VALUES( %s, %s, %s)", (username, email,  password))
        # Commit the changes in DB
        mysql.connection.commit()
        cur.close()
        flash('You are signed up now and you may sign in', 'success')
        return redirect(url_for('signin'))
    return render_template('signup.html', form2=form2)
# User sign in
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Get Form Field
        username = request.form['username']
        password_candidate = request.form['password']
        # Create connection
        cur = mysql.connection.cursor()
        # Get user by username
        result = cur.execute("SELECT * FROM usr WHERE username = %s", [username])
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Check Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed#Session
                session['signed_in'] = True
                session['username'] = username

                flash('You are now signed in', 'success')
                return redirect(url_for('getcoupon'))
            else:
                error = 'Wrong password'
                return render_template('signin.html', error = error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('signin.html', error = error)

    return render_template('signin.html')
# Check customer signed in
def signed_in(g):
    @wraps(g)
    def wrap(*args, **kwargs):
        if 'signed_in' in session:
            return g(*args, **kwargs)
        else:
            flash('Unauthorized, Please sign in', 'danger')
            return redirect(url_for('signin'))
    return wrap
# Signout
@app.route('/signout')
@signed_in
def signout():
    session.clear()
    flash('You are now sign out', 'success')
    return redirect(url_for('signin'))



if __name__ == '__main__':
    app.secret_key='hin'
app.run(debug=True)
