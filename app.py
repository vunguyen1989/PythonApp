from flask import Flask, render_template, request, json, redirect, session
from flask.ext.mysql import MySQL
# from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '#Thankslord@123'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/userHome')
@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')
    
@app.route("/")
def main():
    return render_template('index.html')
    
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')    

@app.route('/signUp',methods=['POST'])
def signUp():
    # create user code will be here !!
    _name = request.form['inputName']
    # print (_name)
    _email = request.form['inputEmail']
    # print (_email)
    _password = request.form['inputPassword']
    # print (_password)
    
    conn = mysql.connect()
    cursor = conn.cursor()

    _hashed_password = _password
    # _hashed_password = generate_password_hash(_password)
    # print (_hashed_password)
    # hash_pass_len = len(_hashed_password)
    # print (hash_pass_len)
    cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
    data = cursor.fetchall()
     
    if len(data) is 0:
        conn.commit()
        return json.dumps({'message':'User created successfully !'})
    else:
        return json.dumps({'error':str(data[0])})
        
@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        
        # connect to mysql
        print (_username)
        print (_password)
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()
        # print (data[0][3])
        
        if len(data) > 0:
            # if check_password_hash(str(data[0][3]),_password):
            if data[0][3] == _password:
                session['user'] = data[0][0]
                return redirect('/userHome')
                # return render_template('userHome.html')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password. 1')
        else:
            return render_template('error.html',error = 'len <= 0, Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()    
    
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/showAddWish')
def showAddWish():
    return render_template('addWish.html')

@app.route('/addWish',methods=['POST'])
def addWish():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')
 
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addWish',(_title,_description,_user))
            data = cursor.fetchall()
 
            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'An error occurred!')
 
        else:
            return render_template('error.html',error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()
 
@app.route('/getWish')
def getWish():
    try:
        if session.get('user'):
            _user = session.get('user')
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))
        
if __name__ == "__main__":
    app.run()