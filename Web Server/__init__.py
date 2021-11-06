from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, jsonify
import bs4 as bs
from xmlfunction import *
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
import MySQLdb
import gc
from functools import wraps
from MySQLdb import escape_string as thwart


app = Flask(__name__)


@app.route('/')
def homepage():
	return render_template("main.html")
	
class RegisterForm(Form):
	name = StringField('System Passcode', [validators.Length(min=1, max=10)])
	username = StringField('NickName', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password')

	


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		controller = form.name.data
		if controller == 'password':
			email = form.email.data
			username = form.username.data
			password = sha256_crypt.encrypt(str(form.password.data))
			# Execute query
			conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
			c = conn.cursor()
			c.execute("INSERT INTO users(username, email, password, controller) VALUES(%s, %s, %s, %s)",
						(thwart(username), thwart(email), thwart(password), thwart(controller)))
			conn.commit()
			c.close()
			conn.close()
			gc.collect()


			flash('You are now registered and can log in', 'success')
			return redirect(url_for('login'))
		else:
			flash('Something went wrong', 'danger')
			return render_template('register.html', form=form)
	return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':
		username_candidate = request.form['username']
		password_candidate = request.form['password']
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()
		result = c.execute("SELECT * FROM users WHERE username = %s", [thwart(username_candidate)])
		conn.close()
		if result > 0:
			data = c.fetchone()[3]
			if sha256_crypt.verify(thwart(password_candidate),data):
				session['logged_in'] = True
				session['username'] = username_candidate
				flash("You Are Now Logged In", "success")
				return redirect(url_for("dashboard"))
			else:
				error = "Wrong Credentials"
				return render_template("login.html", error=error)
		else:
			error="Wrong Credentials"
			return render_template("login.html", error=error)
			
	gc.collect()
	return render_template("login.html")

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap	

	
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('you are now logged out', 'success')
	return redirect(url_for('login'))
	
@app.route('/test', methods=['POST','GET'])
def test():
	if request.method == 'POST':
		device_name = request.form['device_name']
		switch_position = request.form['switch_position']
		status = request.form['status']
		if switch_position == "1":
			if status == "ON":
				query = "UPDATE devices SET switchOneStatus = 0, last_command_one =\"Server - "+ session['username'] +"\" WHERE deviceName = \"" + device_name + "\";"
				#return query
			else:
				query = "UPDATE devices SET switchOneStatus = 1, last_command_one =\"Server - "+ session['username'] +"\" WHERE deviceName = \"" + device_name + "\";"
		elif switch_position == "2":
			if status == "ON":
				query = "UPDATE devices SET switchTwoStatus = 0, last_command_two =\"Server - "+ session['username'] +"\" WHERE deviceName = \"" + device_name + "\";"
			else:
				query = "UPDATE devices SET switchTwoStatus = 1, last_command_two =\"Server - "+ session['username'] +"\" WHERE deviceName = \"" + device_name + "\";"
		
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return redirect(url_for('dashboard'))
		else:
			return 'error'


@app.route('/turnoffall', methods=['POST','GET'])
def turnoffall():
	if request.method == 'POST':
		device_name = request.form['device_name']
		query1 = "UPDATE devices SET switchOneStatus = 0 WHERE deviceName = \"" + device_name + "\";"
		query2 = "UPDATE devices SET switchTwoStatus = 0 WHERE deviceName = \"" + device_name + "\";"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result1 = c.execute(query1)
		conn.commit()
		result2 = c.execute(query2)
		conn.commit()
		conn.close()
		c.close()
		if result2 > 0:
			return 'done'
		else:
			return 'error'

		

	
@app.route('/dashboard', methods=['GET','POST'])
@is_logged_in
def dashboard():
	rows = []
	device = {}
	conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
	c = conn.cursor()
	c.execute("SELECT * FROM devices")
	for data in c.fetchall():
		if data[4] == 1:
			status_one = "ON"
		else:
			status_one = "OFF"
		if data[5] == 1:
			status_two = "ON"
		else:
			status_two = "OFF"
		if data[8] == 0:
			device_status = "OFFLINE"
		else:
			device_status = "ONLINE"
		device = {'device_name': data[6], 'switch_one_name':data[2], 'switch_two_name': data[3], 'status_one': status_one,
					'status_two': status_two, 'device_status' : device_status, 'recent_status_one': data[9], 'recent_status_two': data[10]}
		rows.append(device)                    #[data[6], data[2], data[3], data[4], data[5]]
	conn.close()
	return render_template("dashboard.html", rows = rows)
	
@app.route('/connect', methods=['GET','POST'])
def connect():
	code = '54321'
	return jsonify({'connect':'success'})
	

#under construction	
@app.route('/getdevices', methods=['GET','POST'])
def getdevices():
	if request.method == 'POST':
		rows = []
		device = {}
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()
		c.execute("SELECT * FROM devices")
		for data in c.fetchall():
			device = {'device_name': data[6], 'switch_one_name':data[2], 'switch_two_name': data[3],
						'status_one': data[4], 'status_two': data[5], 'ip_address': data[7], 'device_status': data[8]}
			rows.append(device)                    #[data[6], data[2], data[3], data[4], data[5]]
		conn.close()
		return jsonify(rows)
	else:
		return 'error'

		
@app.route('/postupdate', methods=['POST','GET'])
def postupdate():
	if request.method == 'POST':
		device_name = request.form['device_name']
		switch_position = request.form['switch_position']
		status = request.form['status']
		if switch_position == "1":
			if status == "ON":
				query = "UPDATE devices SET switchOneStatus = 0 WHERE deviceName = \"" + device_name + "\";"
			elif status == "OFF":
				query = "UPDATE devices SET switchOneStatus = 1 WHERE deviceName = \"" + device_name + "\";"
		elif switch_position == "2":
			if status == "ON":
				query = "UPDATE devices SET switchTwoStatus = 0 WHERE deviceName = \"" + device_name + "\";"
			elif status == "OFF":
				query = "UPDATE devices SET switchTwoStatus = 1 WHERE deviceName = \"" + device_name + "\";"
		
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'

@app.route('/sendmyip', methods=['GET','POST'])	
def sendmyip():
	if request.method == "POST":
		content = request.get_json()
		device_name = content['device_name']
		ip_address = content['ip_address']
		#'''
		query = "UPDATE devices SET ipAddress = \"" + ip_address + "\", switchOneStatus = 0, switchTwoStatus = 0 WHERE deviceName = \"" + device_name + "\";"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'
			#'''
		#return jsonify(content)

@app.route('/sendipcontroller', methods=['GET','POST'])		
def sendipcontroller():
	if request.method == "POST":
		content = request.get_json()
		controller_name = content['controller_name']
		ip_address = content['ip_address']
		query = "UPDATE controllers SET ip_address = \"" + ip_address + "\" WHERE controller_name = \"" + controller_name + "\";"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'
		
@app.route('/getipcontroller', methods=['GET','POST'])		
def getipcontroller():
	if request.method == "GET":
		query = "SELECT * FROM controllers;"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		for data in c.fetchall():
			controller_name = data[0]
			controller_ip = data[1]
		conn.close()
		c.close()
		return controller_ip
		

@app.route('/switchhttp', methods=['GET','POST'])		
def switchhttp():
	if request.method == "POST":
		content = request.get_json()
		device_name = content['device_name']
		switch_position = content['switch_position']
		switch_status = content['switch_status']
		if switch_position == "1":
			if switch_status == 0:
				query = "UPDATE devices SET switchOneStatus = 0 WHERE deviceName = \"" + device_name + "\";"
			elif switch_status == 1:
				query = "UPDATE devices SET switchOneStatus = 1 WHERE deviceName = \"" + device_name + "\";"
		elif switch_position == "2":
			if switch_status == 0:
				query = "UPDATE devices SET switchTwoStatus = 0 WHERE deviceName = \"" + device_name + "\";"
			elif switch_status == 1:
				query = "UPDATE devices SET switchTwoStatus = 1 WHERE deviceName = \"" + device_name + "\";"
				
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'

@app.route('/datadump', methods=['GET','POST'])		
def datadump():
	if request.method == "GET":
		rows = []
		device = {}
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()
		c.execute("SELECT * FROM devices;")
		for data in c.fetchall():
			device = {'device_name': data[6], 'switch_one_name':data[2], 'switch_two_name': data[3],
						'status_one': data[4], 'status_two': data[5],'ip_address': data[7]}
			rows.append(device)
		conn.close()
		c.close()
		return jsonify(rows)	

@app.route('/devicestatus', methods=['POST'])	
def devicestatus():
	if request.method == "POST":
		content = request.get_json()
		device_name = content['device_name']
		device_status = content['device_status']
		query = "UPDATE devices SET device_status =" + str(device_status) + " WHERE deviceName=\"" + device_name + "\";"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'
			
@app.route('/recentchange', methods=['POST'])				
def recentchange():
	if request.method == "POST":
		content = request.get_json()
		device_name = content['device_name']
		switch_position = content['switch_position']
		recent_change = content['recent_change']
		if switch_position == 1:
			position = "last_command_one"
		elif switch_position == 2: 
			position = "last_command_two"
		query = "UPDATE devices SET " + position + "=\"" + recent_change + "\" WHERE deviceName=\"" + device_name + "\";"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'
		
@app.route('/adddevice', methods=['POST'])				
def adddevice():
	if request.method == "POST":
		content = request.get_json()
		device_name = content['device_name']
		query = "INSERT INTO devices(deviceName,switchOneName,switchTwoName,switchOneStatus,switchTwoStatus,tempName,ipAddress,device_status,last_command_one,last_command_two) VALUES ('"+device_name+"','Switch1','Switch2',0,0,'"+device_name+"','0.0.0.0',0,'initial','initial');"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'
		
	
@app.route('/removedevice', methods=['POST'])				
def removedevice():
	if request.method == "POST":
		content = request.get_json()
		device_name = content['device_name']
		query = "DELETE FROM devices WHERE deviceName='"+ device_name +"';"
		conn = MySQLdb.connect(host="localhost",user="root",passwd="Password123!", db="myflaskapp")
		c = conn.cursor()	
		result = c.execute(query)
		conn.commit()
		conn.close()
		c.close()
		if result > 0:
			return 'done'
		else:
			return 'error'

		

		
if __name__ == "__main__":
	app.run()


