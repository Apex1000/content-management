from flask import Flask, render_template, flash, redirect, url_for,session,request, logging,jsonify
from flask_pymongo import PyMongo
from wtforms import Form,StringField, TextAreaField, PasswordField, validators, SelectField, DateField, IntegerField, DateTimeField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from flask_paginate import Pagination, get_page_parameter
from flask_paginate import Pagination, get_page_args
import flask_excel as excel
import pyexcel_xls
import json
import datetime
import copy
import webbrowser
from functools import wraps


app = Flask(__name__)

app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('localhost:27017')
db = client.Dashboard
datas = db.datas.find()
users = []
export_id = []
for i in datas:
    users.append(i)
def get_users(offset=0, per_page=8):
    return (users[offset: offset + per_page])

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
@is_logged_in
def index():
    page, per_page, offset = get_page_args(page_parameter='page',
per_page_parameter='per_page')
    users = db.datas.find()
    total=users.count()
    
    pagination_users = users[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    
    return render_template('index.html',
                           users=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
)

@app.route('/search/')
@app.route('/search')
@is_logged_in
def search():
    email = request.args.get('query')
    page, per_page, offset = get_page_args(page_parameter='page',per_page_parameter='per_page')
    users = db.datas.find({'email':{'$all':[{
                                '$elemMatch':{'email':email}
                                }]
                                }})
    total=users.count()
    print (users)
    pagination_users = users[offset: offset + per_page]
    
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html',
                           users=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
)

@app.route('/filter/')
@app.route('/filter')
@is_logged_in
def filter():
    category = request.args.get('category')
    phone_number = request.args.get('phone_number')
    designation = request.args.get('designation')
    pin_code = request.args.get('pin_code')
    
    if phone_number == '' and designation == '' and pin_code == '':
        users = db.datas.find({'category':category}) 
    elif designation == '' and pin_code == '':
        users = db.datas.find({'phone_number':{'$all':[{
                                '$elemMatch':{'number':phone_number}
                                }]
                                },'category':category})
    elif phone_number == '' and designation == '':
        users = db.datas.find({'category':category,'pin_code':pin_code})
    elif phone_number == '' and pin_code == '':
        users = db.datas.find({'category':category,'designation':designation})
    else:
        users = db.datas.find({'address':{'$all':[{
                                '$elemMatch':{'pin_code':pin_code}
                                }]
                                },'category':category,'designation':designation,'phone_number':{'$all':[{
                                '$elemMatch':{'number':phone_number}
                                }]
                                }})
    total = users.count()

    page, per_page, offset = get_page_args(page_parameter='page',per_page_parameter='per_page')
    
    pagination_users = users[offset: offset + per_page]
    
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    
    
    return render_template('index.html',
                           users=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
)
class AddDataForm(Form):
    category = SelectField('Category',choices=[('Professional', 'Professional'), ('Corporate', 'Corporate'), ('Government', 'Government'), ('Institute', 'Institute'), ('Student', 'Student')])
    name = StringField('Name', [validators.Length(min=3, max=35)])
    dob = StringField('DOB  (Format : dd/mm/yyy)',[validators.Length(min=10, max=35)] )
    membership_number = StringField('Membership Number', [validators.Length(min=6, max=15)])
    designation = StringField('Designation', [validators.Length(min=1, max=25)])
    company_name = StringField('Company Name', [validators.Length(min=1, max=25)])
    add1 = StringField('Address', [validators.Length(min=1, max=35)])
    add2 = StringField('Address 2', [validators.Length(min=1, max=35)])    
    add3 = StringField('Address 3', [validators.Length(min=1, max=35)])
    add4 = StringField('Address 4', [validators.Length(min=1, max=35)])
    city = StringField('City', [validators.Length(min=1, max=35)])
    state = StringField('State', [validators.Length(min=1, max=35)])
    region = StringField('Region',[validators.Length(min=1, max=40)])
    pin_code = StringField('Pin code', [validators.Length(min=1, max=35)])
    email = StringField('Email', [validators.Length(min=1, max=35)])
    email1 = StringField('Second Email', [validators.Length(min=1, max=35)])
    phone_number = StringField('Phone Number', [validators.Length(min=1, max=35)])
    landline_number = StringField('Land Line Number', [validators.Length(min=1, max=35)])
    source_of_data = StringField('Source of Data', [validators.Length(min=1, max=35)])
    date_of_creation = StringField('Date of Creation  (Format : dd/mm/yyy)')
    date_of_modification = StringField('Date of Modification  (Format : dd/mm/yyy)')
    file_name = StringField('File Name', [validators.Length(min=1, max=35)])


@app.route('/add_data', methods = ['GET', 'POST'])
@is_logged_in
def adddata():
    form = AddDataForm(request.form)
    if request.method == 'POST':
        category = form.category.data
        name = form.name.data
        dob = form.dob.data
        membership_number = form.membership_number.data
        designation = form.designation.data
        company_name = form.company_name.data
        add1 = form.add1.data
        add2 = form.add2.data
        add3 = form.add3.data
        add4 = form.add4.data
        city = form.city.data
        state = form.state.data
        region = form.region.data
        pin_code = form.pin_code.data
        email = form.email.data
        email1 = form.email1.data
        phone_number = form.phone_number.data
        landline_number = form.landline_number.data
        source_of_data = form.source_of_data.data
        date_of_creation = form.date_of_creation.data
        date_of_modification = form.date_of_modification.data
        file_name = form.file_name.data
        existing_email = db.datas.find_one({'email':{'$all':[{
                                '$elemMatch':{'email':email}
                                }]
                                }})
        existing_phone = db.datas.find_one({'phone_number':{'$all':[{
                                '$elemMatch':{'number':phone_number}
                                }]
                                }})

        # if (existing_email is not None and existing_email['category']!=category )
        if (existing_email is None):
            data = {
                'category' : category,
                'name' : name,
                'dob' : dob,
                'membership_number' : membership_number,
                'designation' : designation,
                'company_name' : company_name,
                'address':[{
                    'add1' : add1,
                    'add2' : add2,
                    'add3' : add3,
                    'add4' : add4,
                    'city' : city,
                    'state' : state,
                    'region' : region,
                    'pin_code' : pin_code
                }],
                'email' : [{'email' : email},{'email' : email1}],
                'phone_number' : [{
                    'number' : phone_number
                    }],
                'landline_number' : landline_number,
                'source_of_data' : source_of_data,
                'date_of_creation' : date_of_creation,
                'date_of_modification' : date_of_modification,
                'file_name' : file_name
            }
            db.datas.insert_one(data)
        else:
            db.datas.update({'email':{'$all':[{
                                '$elemMatch':{'email':email}
                                }]
                                }},{'$push':{
                'address':{
                    'add1' : add1,
                    'add2' : add2,
                    'add3' : add3,
                    'add4' : add4,
                    'city' : city,
                    'state' : state,
                    'region' : region,
                    'pin_code' : pin_code
                }
            }})
            if (existing_phone is None):
                db.datas.update({'email':{'$all':[{
                                '$elemMatch':{'email':email}
                                }]
                                }},{'$push':{
                'phone_number':{
                    'number' : phone_number
                }
            }})
        flash('New Record Added', 'success')
        return redirect(url_for('index'))
    return render_template('./adddata.html',form=form)

@app.route('/edit/<string:id>', methods=['POST','GET'])
@is_logged_in
def edit(id):
    
    form = AddDataForm(request.form)
    existing_email = db.datas.find_one({'email':{'$all':[{
                                '$elemMatch':{'email':id}
                                }]
                                }})

    form.category.data = existing_email['category']
    form.name.data = existing_email['name']
    form.dob.data = existing_email['dob']
    form.membership_number.data = existing_email['membership_number']
    form.designation.data = existing_email['designation']
    form.company_name.data = existing_email['company_name']
    form.add1.data = existing_email['address'][0]['add1']
    form.add2.data = existing_email['address'][0]['add2']
    form.add3.data = existing_email['address'][0]['add3']
    form.add4.data = existing_email['address'][0]['add4']
    form.city.data = existing_email['address'][0]['city']
    form.state.data = existing_email['address'][0]['state']
    form.region.data = existing_email['address'][0]['region']
    form.pin_code.data = existing_email['address'][0]['pin_code']
    form.email.data = existing_email['email'][0]['email']
    form.email1.data = existing_email['email'][1]['email']
    form.phone_number.data = existing_email['phone_number'][0]['number']
    form.landline_number.data = existing_email['landline_number']
    form.source_of_data.data = existing_email['source_of_data']
    form.date_of_creation.data = existing_email['date_of_creation']
    # form.date_of_modification.data = existing_email['date_of_modification']
    form.file_name.data = existing_email['file_name']



    if request.method == 'POST':
        category = request.form['category']
        name = request.form['name']
        dob = request.form['dob']
        membership_number = request.form['membership_number']
        designation = request.form['designation']
        company_name = request.form['company_name']
        add1 = request.form['add1']
        add2 = request.form['add2']
        add3 = request.form['add3']
        add4 = request.form['add4']
        city = request.form['city']
        state = request.form['state']
        region = request.form['region']
        pin_code = request.form['pin_code']
        email = request.form['email']
        email1 = request.form['email1']
        phone_number = request.form['phone_number']
        landline_number = request.form['landline_number']
        source_of_data = request.form['source_of_data']
        date_of_creation = request.form['date_of_creation']
        # date_of_modification = request.form['date_of_modification']
        file_name = request.form['file_name']
        print (id)
        db.datas.delete_one({'email':{'$all':[{
                                '$elemMatch':{'email':id}
                                }]
                                }})
        update_record = {
                    'category' : category,
                    'name' : name,
                    'dob' : dob,
                    'membership_number' : membership_number,
                    'designation' : designation,
                    'company_name' : company_name,
                    'address':[{
                        'add1' : add1,
                        'add2' : add2,
                        'add3' : add3,
                        'add4' : add4,
                        'city' : city,
                        'state' : state,
                        'region' : region,
                        'pin_code' : pin_code
                    }],
                    'email' : [{'email' : email},{'email' : email1}],
                    'phone_number' : [{
                        'number' : phone_number
                        }],
                    'landline_number' : landline_number,
                    'source_of_data' : source_of_data,
                    'date_of_creation' : date_of_creation,
                    # 'date_of_modification' : date_of_modification,
                    'file_name' : file_name
                }
        
        db.datas.insert_one(update_record)
        print (update_record)
        flash('Record Edited', 'success')
        return redirect(url_for('index'))

        print (update_record)

    return render_template('./edit_data.html',form=form)

@app.route('/delete/<string:id>', methods=['POST'])
@is_logged_in
def delete(id):
    existing_email = db.datas.delete_one({'email':{'$all':[{
                                '$elemMatch':{'email':id}
                                }]
                                }})
    flash('Record Deleted', 'danger')
    return redirect(url_for('index'))


class Uploaddata(Form):
    category = SelectField('Category',choices=[('Professional', 'Professional'), ('Corporate', 'Corporate'), ('Government', 'Government'), ('Institute', 'Institute'), ('Student', 'Student')])


@app.route('/upload', methods=['POST','GET'] )
@is_logged_in
def upload():
    dd = []
    form = Uploaddata()
    if request.method == 'POST':
        result = request.get_array(field_name='file')
        for i in result:
            data = {
                'category' : i[0],
                'name' : i[1],
                'dob' : str(i[3]),
                'membership_number' : i[2],
                'designation' : i[4],
                'company_name' : i[5],
                'address':[{
                    'add1' : i[6],
                    'add2' : i[7],
                    'add3' : i[8],
                    'add4' : i[9],
                    'city' : i[10],
                    'state' : i[11],
                    'region' : i[20],
                    'pin_code' : str(i[12])
                }],
                'email' : [{'email' : i[13]},{'email' : i[14]}],
                'phone_number' : [{
                    'number' : str(i[15])
                    }],
                'landline_number' : i[16],
                'source_of_data' : str(i[17]),
                'date_of_creation' : str(i[18]),
                'file_name' : i[19]
            }

            db.datas.insert_one(data)
        flash('New File Uploaded.', 'success')
        return redirect(url_for('index'))
    return render_template('./upload.html', form=form)

@app.route('/export')
@is_logged_in
def export():
    category = request.args.get('category')
    phone_number = request.args.get('phone_number')
    designation = request.args.get('designation')
    pin_code = request.args.get('pin_code')
    
    if phone_number == '' and designation == '' and pin_code == '':
        users = db.datas.find({'category':category}) 
    elif designation == '' and pin_code == '':
        users = db.datas.find({'phone_number':{'$all':[{
                                '$elemMatch':{'number':phone_number}
                                }]
                                },'category':category})
    elif phone_number == '' and designation == '':
        users = db.datas.find({'category':category,'pin_code':pin_code})
    elif phone_number == '' and pin_code == '':
        users = db.datas.find({'category':category,'designation':designation})
    else:
        users = db.datas.find({'address':{'$all':[{
                                '$elemMatch':{'pin_code':pin_code}
                                }]
                                },'category':category,'designation':designation,'phone_number':{'$all':[{
                                '$elemMatch':{'number':phone_number}
                                }]
                                }})
    total = users.count()
    print (total)
    de = [[(users[i]['category']),
    (users[i]['name']),
    (users[i]['dob']),
    (users[i]['membership_number']),
    (users[i]['designation']),
    (users[i]['company_name']),
    # for j in range(i):
    (users[i]['address'][0]['add1']),
    (users[i]['address'][0]['add2']),
    (users[i]['address'][0]['add3']),
    (users[i]['address'][0]['add4']),
    (users[i]['address'][0]['city']),
    (users[i]['address'][0]['state']),
    (users[i]['address'][0]['region']),
    (users[i]['address'][0]['pin_code']),
    # for j in range(i):
    (users[i]['email'][0]['email']),
    (users[i]['email'][1]['email']),
    # for j in range(i):
    (users[i]['phone_number'][0]['number']),
    (users[i]['landline_number']),
    (users[i]['source_of_data']),
    (users[i]['date_of_creation']),
    #(users[i]['date_of_modification']),
    (users[i]['file_name'])]for i in range(total)]
	
    return excel.make_response_from_array(de, "csv",
                                          file_name="export_data")
    # return excel.make_response_from_array(export_id, "csv",
    #                                       file_name="export_data")

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    types = SelectField('Category',choices=[('user', 'User'), ('superuser', 'superuser')])
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
        login = db.users.find()
        name = form.name.data
        types = form.types.data
        username = form.username.data
        password = form.password.data
        data = {
                'name' : name,
                'username' : username,
                'types' : types,
                'password' : password
            }
        db.users.insert_one(data)

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = db.users.find_one({'username':username})

        # Get user by username
        result = len(cur)

        if result > 0:
            # Get stored hash
            password = cur['password']

            # Compare Passwords
            if password_candidate == password:
                # Passed
                session['logged_in'] = True

                session['username'] = username
                session['types'] = cur['types']

                flash('You are now logged in ' + cur['types'], 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/backup')
@is_logged_in
def backup():
    users = db.datas.find()
    total = users.count()
    print (total)
    de = [[(users[i]['category']),
    (users[i]['name']),
    (users[i]['dob']),
    (users[i]['membership_number']),
    (users[i]['designation']),
    (users[i]['company_name']),
    # for j in range(i):
    (users[i]['address'][0]['add1']),
    (users[i]['address'][0]['add2']),
    (users[i]['address'][0]['add3']),
    (users[i]['address'][0]['add4']),
    (users[i]['address'][0]['city']),
    (users[i]['address'][0]['state']),
    (users[i]['address'][0]['region']),
    (users[i]['address'][0]['pin_code']),
    # for j in range(i):
    (users[i]['email'][0]['email']),
    (users[i]['email'][1]['email']),
    # for j in range(i):
    (users[i]['phone_number'][0]['number']),
    (users[i]['landline_number']),
    (users[i]['source_of_data']),
    (users[i]['date_of_creation']),
    #(users[i]['date_of_modification']),
    (users[i]['file_name'])]for i in range(total)]
    
    return excel.make_response_from_array(de, "csv",
                                          file_name="export_data")


if __name__=='__main__':
    excel.init_excel(app)
    a_website = 'http://localhost:5000/'
    webbrowser.open_new(a_website)
    app.run(debug=True)
