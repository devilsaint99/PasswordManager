from flask import Flask,render_template,request,redirect,url_for, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import rsa

app=Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


app.secret_key = 'devilsaint'
app.permanent_session_lifetime = timedelta(minutes=15)

db = SQLAlchemy(app)

class Users(db.Model):
    _id=db.Column('id', db.Integer, primary_key=True)
    user=db.Column(db.String(100),unique=True)
    pwd=db.Column(db.String(100))

    def __init__(self, user, pwd):
        self.user=user
        self.pwd=pwd


class Credentials(db.Model):
    _id=db.Column('id', db.Integer, primary_key=True)
    owner=db.Column(db.String(100),nullable=False)
    website=db.Column(db.String(250),nullable=False)
    user=db.Column(db.String(250),nullable=False)
    email_id=db.Column('email', db.String(100),nullable=False)
    pwd=db.Column('password', db.String(250),nullable=False)

    def __init__(self,owner, website, user, email_id, pwd):
        self.owner=owner
        self.website=website
        self.user=user
        self.email_id=email_id
        self.pwd=pwd
        
@app.route("/")
def home():        
    return redirect(url_for('login'))

@app.route("/register", methods=['POST','GET'])
def register():
    """registraiton"""
    try:
        if request.method=='POST':
            user=request.form['user']
            pwd=bcrypt.generate_password_hash(request.form['password'])

            register_user=Users(user, pwd)
            db.session.add(register_user)
            db.session.commit()
            flash("Registration was successfull.")
            return redirect(url_for('login'))
    except:
        flash("User already exists")
        return redirect(url_for('register'))

    return render_template('register.html')


@app.route("/login", methods=['POST','GET'])
def login():
    """Login Page"""

    

    # cred={'user':'Anshul','pwd':'123qwerty'}                                               #test credentials
    if request.method=='POST':                                                                   ## get data from form 
        user=request.form["user"]                                                      #get username
        password=request.form["password"] 
        
        result=db.session.query(Users).filter(Users.user==user)
       
            
        for row in result:
            try:     
                if user==row.user and bcrypt.check_password_hash(row.pwd, password):                   #authenticate
                    session.permanent = True    
                    session['user'] = user
                    flash("You are logged in!!", "info")           
                    return redirect(url_for("logged"))             
                else:
                    return render_template("login.html")
            except:
                flash('No such user exists!!')
                return redirect(url_for('login'))
    if 'user' in session:
        flash(f"You are already logged in as {session['user']}")
        return redirect(url_for('logged'))
    return render_template('login.html')


@app.route("/logged")
def logged():
    if 'user' in session:
        all_cred=db.session.query(Credentials).filter(Credentials.owner==session['user'])
        return render_template("logged.html",all_cred=all_cred)
    else:
        flash("Please Login!!","info")
        return redirect(url_for('login'))

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    update_details=db.session.query(Credentials).filter(Credentials._id==id)
    if request.method=='POST':
        for row in update_details:
            row.website=request.form['website']
            row.user=request.form['username']
            row.email_id=request.form['email']
            row.pwd=request.form['pwd']
        db.session.commit()
        return redirect(url_for('logged'))
    
    return render_template("update.html",update_details=update_details)

@app.route("/delete/<int:id>")
def delete(id):
    delete_details=db.session.query(Credentials).filter(Credentials._id==id)
    for row in delete_details:
        db.session.delete(row)
    db.session.commit()
    return redirect(url_for('logged'))


@app.route("/add_credentials", methods=['POST','GET'])
def add_credentials():
    if 'user' in session:
        if request.method=='POST':
            owner=session['user']
            website=request.form['website']
            user=request.form['user']
            email=request.form['email']
            pwd=request.form['password']

            add_details=Credentials(owner, website, user, email, pwd)
            db.session.add(add_details)
            db.session.commit()

        return render_template('add.html')

    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if 'user' in session:
        flash("You have been logged out", "warning")
    session.pop('user',None)
    return redirect(url_for('login'))



@app.route('/test')
def test():
    user='asd'
    password='sad'
    result=db.session.query(Users).filter(Users.user==user, Users.pwd==password)
    dic={}
    for row in result:
        dic['user']=row.user
        dic['pwd']=row.pwd 
    
    return render_template('test.html') 


if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
    