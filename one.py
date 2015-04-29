from flask import Flask, request, render_template, redirect, url_for, session
from flask_pymongo import PyMongo
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
from werkzeug import secure_filename
from random import randint
import os

app=Flask(__name__)

app.secret_key = 'dfgsdfgsfgdfsg'
UPLOAD_FOLDER = '~/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['MONGO_HOST'] = '0.0.0.0'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = 'test'
mongo = PyMongo(app)

global this_user

@app.route('/')
def home():
#	a = 5
#	import pdb
#	pdb.set_trace()
    return render_template("home.html")

@app.route('/hide',methods=['POST','GET'])
def hide():
    hi = request.args.get("hide")
    print 'there'
    print hi

    return redirect(url_for('member'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/delete',methods=['POST','GET'])
def delete():
    email=this_user
    usernam = mongo.db.users.find({"email":{ '$regex' : email}})
    for d in usernam:
        use= d['username']
    myvar = request.args.get("image_id")
    user_details = mongo.db.contents.find({'username': {'$regex': use}})
    for u_d in user_details:
        items = u_d['items']
        items = [x for x in items if not (int(myvar) == int(x.get('im_id')))]
        #sort a list of dict in desc
        items = sorted(items, key=lambda x: x.get('im_id'), reverse=True)

    i={"username":use,'items':items}
    mongo.db.contents.remove( { 'username': use }  )
    mongo.db.contents.insert(i)
                
    #mongo.contents.find({'im_id': {'$regex': myvar}})
    return redirect(url_for('profile'))


@app.route('/upload',methods=['POST','GET'])
def upload():
    error= None
    if request.method== 'POST':
        email=this_user
        usernam = mongo.db.users.find({"email":{ '$regex' : email}})
        use=''
        for d in usernam:
            use= d['username']
        print use
        
      
        file = request.files['file']
        filename = secure_filename(file.filename)
        s=filename.split('.')[0]
        fname=s+str(randint(10000,99999)) + '.jpg'
        file.save('./static/images/' + fname)
       
        head= request.form['shortdesc']
        description= request.form['longdesc']
        data=mongo.db.contents.find()
        names=[]
        for usernames in data:
            y=usernames['username']
            names.append(y)
        
        #print names
            
        #print use
        if use not in names:
            rand_number = randint(1000000, 9999999)
            y={'username':use,"head":head,"description":description, 'im_id': rand_number, 'image':fname}
            j=[]
            j.append(y)
            new={'username':use,'items':j}
            mongo.db.contents.insert(new)
        else:
            rand_number  = randint(1000000, 9999999)
            y={'username':use,"head":head,"description":description, 'im_id': rand_number, 'image':fname}
            j=[]
            j.append(y)
            u=usernames['items']
            u=u+j
            usernames['items']=u
            new_items=usernames['items']
            i={"username":use,'items':new_items}
            mongo.db.contents.remove( { 'username': use }  )
            mongo.db.contents.insert(i)

           
    return render_template('upload.html', error=error) 
    


@app.route('/member')
def member():
    #x='{'+'email:'+ "'" + this_user + "'" +'}'
	data= mongo.db.contents.find()
    #print data
	return render_template("member.html",obj=data)


@app.route('/profile')
def profile(): 
    email=this_user
    usernam = mongo.db.users.find({"email":{ '$regex' : email}})
    for d in usernam:
        use= d['username']

    print use
    dat = mongo.db.contents.find()
    return render_template("profile.html", obj=dat , username=use)


@app.route('/login',methods=['GET','POST'])
def login(): 
    error= None
    if request.method== 'POST':
        this_user=request.form['email']
        globals()['this_user']= request.form['email']
        this_password=request.form['password']
        print this_user
        print this_password
        data=mongo.db.users.find()
        k=0
        for user in data:
            if (user['email']== this_user and user['password']==this_password):
                k=1
                session['logged_in']= True
                return redirect(url_for('member'))
            else:
                error='Invalid credentials.Please try again!'

        if(k==1):
            error= None

    return render_template('login.html', error=error)

    #data=mongo.db.testData.find()
    #return render_template("login.html",obj=data)
    #return j
    #return render_template("login.html")



@app.route('/register',methods=['GET','POST'])
def register():
    error=None
    data= mongo.db.users.find()
    if request.method== 'POST':
        k=0
        data=mongo.db.users.find()
        this_fn=user= request.form['firstname']
        this_ln= request.form['lastname']
        this_user= request.form['email']
        #globals()['this_user']= request.form['email']
        this_password= request.form['password']
        username= this_fn + this_ln
        for user in data:
            if(user['email']==this_user):
                error='User already exists! Please use a different email ID.'
                return render_template('register.html',error=error)
            else:
                k=1
                #x= "'"+ name + "'" + ':' + '[' + "firstname" + ':' + "'" + this_fn + "'," + "lastname" + ':' + "'"+ this_ln + "'," + "email" + ':' +  "'" + this_user +  "'," + "password" + ':' + "'" + this_password + "'" + ']'
                x = {"firstname" :  this_fn, "lastname": this_ln, "email": this_user, "password":  this_password, "username": username }
                mongo.db.users.insert(x)
                return redirect(url_for('login'))
        
        if(k==1):
            error= None

    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    this_user=''
    return redirect(url_for('login'))



@app.route('/loggedout')
def loggedout():
    return render_template('loggedout.html')

#x

if __name__== '__main__':
    app.run(host='0.0.0.0', port=8080,debug='true')
