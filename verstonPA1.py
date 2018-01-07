# -*- coding: utf-8 -*-
from flask import *
from sql import Sql
from flask_login import LoginManager, login_user, login_required, logout_user
import json, re

from user import User

app = Flask(__name__)


# configuration
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# Classes
sql = Sql(app) # sql

# login and user management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(userid):
    sqla = "select iduser, user_username, user_name, user_surname, user_password from user where iduser = %s limit 1"
    result = sql.execute(sqla, userid)
    return populate_user(result)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sqla = "select iduser, user_username, user_name, user_surname, user_password from user where user_username = %s limit 1"
        result = sql.execute(sqla, username)
        print result

        user = populate_user(result)
        if user:

            if password == user.password:
                login_user(user)
                return redirect(request.args.get("next"))

    return render_template('login.html')


def populate_user(result):
    if result:
        id = result[0][0]
        username = result[0][1]
        name = result[0][2]
        surname = result[0][3]
        password = result[0][4]
        password = name
        return User(id=id, name=name, password=password, surname=surname, username=username)
    return None

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/data')
def datatables():
    return render_template('datatablestest.html')


@app.route('/data/get', methods=['POST', 'GET'])
def datatables_json():
    if request.method == 'POST':

        request_data = json.dumps(request.form)
        obj = json.loads(request_data)

        a = obj.keys()[1]  # a = key of 2nd item (0 is first) in json dict (a complex string needs further parse)
        d = obj.values()[1]  # d = value for the previously mentioned key (actual VALUE of FIELD to be UPDATED)

        # b is a result of further parse of a (containing both element id in database and field name to be updated)
        # regular expression search is performed, resulting a LIST of id and a field name to be updated
        b = re.findall(r"\[([A-Za-z0-9_]+)\]", a)

        # c is a dictionary containing 2 pairs of field:value id:b[0] and b[1]:d
        c = {}
        c['idtablename'] = '`user`'
        c['idfieldname'] = 'iduser'
        c['idfieldvalue'] = b[0]
        c['fieldname'] = b[1]
        c['fieldvalue'] = d

        # update sql formed here
        # sqla = 'UPDATE ' + c['idtablename'] + ' SET ' + c['fieldname'] + '="' + c['fieldvalue'] + '" WHERE ' + c['idfieldname'] + ' = "' + c['idfieldvalue'] +'"'

        sqla = "UPDATE " + c['idtablename'] + " SET " + c['fieldname'] + " = %s WHERE " + c['idfieldname'] + "= %s"
        values = c['fieldvalue'], c['idfieldvalue']
        result1 = sql.execute(sqla, values)

        sqlb = "SELECT \
                          iduser, user_name, user_position, user_positions_name \
                          FROM user, user_groups, user_positions \
                          WHERE \
                          user_usergroup = iduser_groups AND user_position = iduser_positions AND iduser = %s"
        result2 = sql.run_query_json(sqlb, c['idfieldvalue'])

        # print ("---------")
        print ("Request form: ")
        #
        #
        print request.form
        # print ("Request form: action extract: ", request.form['action'])
        # print ("Request form: Json dump: ", request_data)
        # print ("Request form: Json dump: 1st data entry: ", request_data[1])
        # print ("Request Json load: ")
        # print obj
        # print ("Request Json load: 1'st item on Json load:")
        # print obj.keys(), obj.values()
        # print ("Request Json load: 1'st item on Json load keys list: ")
        # print b
        # print ("dictionary containing 2 pairs of field:value id:b[0] and b[1]:d")
        # print c
        # print ("sql created: " , values)
        # print result2
        return result2

    else:
        sqla = "SELECT \
                  iduser, user_name, user_position, user_positions_name \
                  FROM user, user_groups, user_positions \
                  WHERE \
                  user_usergroup = iduser_groups AND user_position = iduser_positions"
        result = sql.run_query_json(sqla, None)
        return result


@app.route('/objects')
@login_required
def pa_objects():
    sqla = "select idobject, shiffer,name,obj_manager, proj_manager, `begin`,end_planned,end_true,overhead_rate,`status`,changed_date from object"
    result = sql.run_query(sqla)
    return render_template('objects.html', result=result, amount=len(result))

# see on lihtne redirect testimise eesmärgil, kuhu saab süütult postida asju
@app.route('/test', methods=['POST'])
def test():
    print ("test done")
    return redirect(url_for('users'))


# see on endpoint, mille abil veendutakse ega ei eksisteeri juba kasutajat, väljastab JSONI "validate" key-ga
@app.route('/validate', methods=['POST'])
@login_required
def user_check():
    sqla = "select 1 from user where user_username = %s limit 1"
    value = request.form ['username']
    exists = sql.execute(sqla, value)
    if exists:
        return json.dumps({'validate':'exists'})
    else:
        return json.dumps({'validate':'ok'})


# see on kasutajate näitamiseks
@app.route('/users')
@login_required
def users():
    sqla = "select \
            iduser, user_worker_begin_id, user_name, user_surname, \
            user_username, user_usergroup, user_position, user_status, user_lastchanged, \
            user_group_name, user_positions_name \
            from user, user_groups, user_positions \
            where \
            user_usergroup = iduser_groups and user_position = iduser_positions"
    sqlb = "select * from user_groups where user_group_status > 1"
    sqlc = "select * from user_positions where user_positions_status > 1"
    users = sql.run_query(sqla)
    groups = sql.run_query(sqlb)
    positions = sql.run_query(sqlc)
    return render_template('users.html', users=users, amount=len(users), groups=groups, positions=positions)


# see on samal templatel kasutajate manipuleerimiseks
@app.route('/users', methods=['POST'])
@login_required
def save_user():
    if not request.form ['id']:
        sqla = "insert into user (user_name,user_surname,user_username,user_position,user_usergroup, user_status) values (%s, %s, %s, %s, %s, %s)"
        values = (request.form['name'], request.form['surname'], request.form['email'], request.form['position'], request.form ['group'], 3)
        sql.execute(sqla, values)

    else:
        sqla = "update user set user_name = %s, user_surname = %s,user_username = %s, user_position=%s,user_usergroup =%s where iduser = %s"
        values = (request.form['name'], request.form['surname'], request.form['email'], request.form['position'],
                  request.form['group'],request.form ['id'] )
        sql.execute(sqla, values)

    return redirect(url_for('users'))


# see on objektide lehe näitamise loogika - siia sama põhimõte kui
@app.route('/object/<code>')
@login_required
def pa_object(code):
    sqla = "select * from offer"
    income = sql.run_query(sqla)
    print income
    return render_template('object.html', income=income, shiffer=code)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
