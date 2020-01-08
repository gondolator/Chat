from flask import Flask, render_template, url_for, flash, redirect, jsonify, current_app
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask import request
from forms import InputForm, LoginForm, RegisterForm
from pandas.io.json import json_normalize
from werkzeug.utils import secure_filename
#from myScripts.transformer import ProcessRiskDescriptionTransformer, process_riskID, process_riskCat, ProcessRiskIDTransformer, ColumnSelector, ProcessRiskDescriptionTransformer, ProcessRiskIDTransformer, DenseTransformer

import re
import flask
import pandas as pd
import json
import requests
import sys
import os
import datetime
import sqlite3
import ssl
import http.server

#code which helps initialize our server
app = Flask(__name__)

certificate_file = './certificate.pem'
private_key_file = './privkey.pem'


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'C:\\Users\\z003udrm\\source\\Python\\flask\\Chat\\static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = '04e1de6ef2ee79d83ea1a9cf966f7e43'
app.config['SQLAlchemy_DATABASE_URI'] = 'sqlite:///C:\\Users\\z003udrm\\source\\Python\\flask\\Chat\\ChatServer.db'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __table_name__ = 'Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()

    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class

        conn = sqlite3.connect('ChatServer.db')
        conn.row_factory = sqlite3.Row
        wert = conn.cursor()
        wert.execute('SELECT ID FROM Accounts WHERE Benutzername = ? AND Passwort = ?', (form.Benutzername.data, form.Passwort.data))
        rv = wert.fetchall()
        conn.close()
        if len(rv) > 0:
            user = User()
            user.id = rv[0]['ID']
            user.username = form.Benutzername.data
            #user.authenticated = True
            try:
                db.session.add(user)
                db.session.commit()
                login_user(user)
            except:
                login_user(user)

            return redirect(url_for('index'))
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        #if not is_safe_url(next):
        #    return flask.abort(400)
    return render_template('login.html', title='test', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = RegisterForm()

    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class

        conn = sqlite3.connect('ChatServer.db')
        conn.row_factory = sqlite3.Row
        wert = conn.cursor()
        wert.execute('SELECT ID FROM Accounts WHERE Benutzername = ?', (form.Benutzername.data,))
        rv = wert.fetchall()
        if len(rv) == 0:
            if(form.Passwort.data == form.Passwort2.data):
                wert.execute('INSERT INTO Accounts(Benutzername, Passwort) VALUES(?, ?)', (form.Benutzername.data, form.Passwort.data))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        #if not is_safe_url(next):
        #    return flask.abort(400)
        conn.close()

    return render_template('register.html', title='test', form=form)

@app.route('/', methods=['GET', 'POST'])
def routing():
    return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    conn = sqlite3.connect('ChatServer.db')
    conn.row_factory = sqlite3.Row
    wert = conn.cursor()
    wert.execute('WITH cte AS ( SELECT s.Benutzername as Sender, r.Benutzername as Empfaenger, n.Inhalt, n.Zeit FROM Nachrichten as n LEFT JOIN Accounts as r ON n.Empfaenger = r.ID LEFT JOIN Accounts as s ON n.Sender = s.ID WHERE ? IN (s.Benutzername, r.Benutzername)), lastdates as (SELECT CASE WHEN ? = c.Empfaenger THEN c.Sender WHEN ? = c.Sender THEN c.Empfaenger END other, MAX(c.Zeit) maxdate FROM cte c GROUP BY other ) SELECT c.* FROM cte c inner join lastdates l ON l.other in (c.Empfaenger, c.Sender) AND l.maxdate = c.Zeit order by c.Zeit desc', (current_user.username, current_user.username, current_user.username))
    rv = wert.fetchall()
    conn.close()
    return render_template('index.html', error=rv, username=current_user.username)

@app.route('/Contacts', methods=['GET', 'POST'])
@login_required
def Contacts():
    conn = sqlite3.connect('ChatServer.db')
    conn.row_factory = sqlite3.Row
    wert = conn.cursor()
    wert.execute('SELECT Accounts.Benutzername, Contacts.Blockiert FROM Contacts LEFT JOIN Accounts ON Contacts.Kontaktname = Accounts.ID LEFT JOIN Accounts as Accounts_2 On Contacts.Benutzername = Accounts_2.ID WHERE Accounts_2.Benutzername = ?', (current_user.username,))
    rv = wert.fetchall()
    conn.close()
    return render_template('Contacts.html', error=rv)

@app.route('/AddContact', methods=['POST'])
@login_required
def AddContact():
    name = request.form['Benutzername']
    conn = sqlite3.connect('ChatServer.db')
    conn.row_factory = sqlite3.Row
    wert = conn.cursor()
    if name == current_user.username:
        return redirect(url_for('Contacts'))

    wert.execute('SELECT COUNT(*) FROM Contacts LEFT JOIN Accounts ON Contacts.Kontaktname = Accounts.ID LEFT JOIN Accounts as Accounts_2 On Contacts.Benutzername = Accounts_2.ID WHERE Accounts_2.Benutzername = ? AND Accounts.Benutzername = ?', (current_user.username, name))
    rv = wert.fetchall()
    if rv[0][0] > 0:
        return redirect(url_for('Contacts'))

    wert.execute('SELECT COUNT(*) FROM Accounts WHERE Accounts.Benutzername = ?', (name,))
    rv = wert.fetchall()
    if rv[0][0] == 0:
        return redirect(url_for('Contacts'))

    wert1 = conn.cursor()
    wert2 = conn.cursor()
    wert1.execute('Select ID From Accounts WHERE Accounts.Benutzername = ?', (current_user.username,))
    wert2.execute('Select ID From Accounts WHERE Accounts.Benutzername = ?', (name,))
    rv1 = wert1.fetchall()
    rv2 = wert2.fetchall()
    wert.execute('INSERT INTO Contacts(Benutzername, Kontaktname, Blockiert) VALUES(?, ?, 0)', (rv1[0]['ID'], rv2[0]['ID']))
    conn.commit()
    conn.close()
    return redirect(url_for('Contacts'))


@app.route('/Chat', methods=['POST', 'GET'])
@login_required
def forms():
    conn = sqlite3.connect('ChatServer.db')
    conn.row_factory = sqlite3.Row
    wert = conn.cursor()
    if request.method == 'POST':
        button = request.form['action']
        print(button)
        if button == 'NeuChat':
            return render_template('NewGroupChat.html', title='test')
        else:
            wert.execute('SELECT Inhalt, Zeit, Accounts_2.Benutzername as Sender FROM Nachrichten LEFT JOIN Accounts ON Nachrichten.Empfaenger = Accounts.ID LEFT JOIN Accounts as Accounts_2 On Nachrichten.Sender = Accounts_2.ID WHERE (Accounts_2.Benutzername = ? AND Accounts.Benutzername = ?) OR (Accounts.Benutzername = ? AND Accounts_2.Benutzername = ?)', (current_user.username, button, current_user.username, button))
            rv = wert.fetchall()
    else:
        button = request.args['submit']
        if request.args['Benutzername'] == "":
            return render_template('forms.html', title='test')

        wert1 = conn.cursor()
        wert2 = conn.cursor()
        wert1.execute('Select ID From Accounts WHERE Accounts.Benutzername = ?', (current_user.username,))
        wert2.execute('Select ID From Accounts WHERE Accounts.Benutzername = ?', (button,))
        rv1 = wert1.fetchall()
        rv2 = wert2.fetchall()
        wert.execute('INSERT Into Nachrichten(Sender, Empfaenger, Zeit, Inhalt) Values(?, ?, ?, ?)', (rv1[0]['ID'], rv2[0]['ID'], datetime.datetime.now(), request.args['Benutzername']))
        conn.commit()
        wert.execute('SELECT Inhalt, Zeit, Accounts_2.Benutzername as Sender FROM Nachrichten LEFT JOIN Accounts ON Nachrichten.Empfaenger = Accounts.ID LEFT JOIN Accounts as Accounts_2 On Nachrichten.Sender = Accounts_2.ID WHERE (Accounts_2.Benutzername = ? AND Accounts.Benutzername = ?) OR (Accounts.Benutzername = ? AND Accounts_2.Benutzername = ?)', (current_user.username, button, current_user.username, button))
        rv = wert.fetchall()
        #return redirect(url_for('index2', error = Jsonstr))
        return render_template('forms.html', title='test', error=button, Nachrichten=rv)
    wert.execute('Select Blockiert from Contacts Where Contacts.Benutzername = (Select ID from Accounts where Accounts.Benutzername = ?) AND Contacts.Kontaktname = (Select ID from Accounts where Accounts.Benutzername = ?)', (button, current_user.username))
    rv3 = wert.fetchall()
    try:
        if rv3[0]['Blockiert'] == 1:
            conn.close()
            return render_template('forms.html', title='test')
    except:
        rv3 = wert.fetchall()

    wert.execute('Select Blockiert from Contacts Where Contacts.Benutzername = (Select ID from Accounts where Accounts.Benutzername = ?) AND Contacts.Kontaktname = (Select ID from Accounts where Accounts.Benutzername = ?)', (current_user.username, button))
    rv3 = wert.fetchall()
    try:
        if rv3[0]['Blockiert'] == 1:
            conn.close()
            return render_template('forms.html', title='test')
    except:
        rv3 = wert.fetchall()
    conn.close()
    return render_template('forms.html', title='test', error=button, Nachrichten=rv)

@app.route('/RLChat', methods=['POST'])
@login_required
def RT():
    conn = sqlite3.connect('ChatServer.db')
    wert = conn.cursor()
    button = request.form['submit']
    wert.execute('SELECT Inhalt, Zeit, Accounts_2.Benutzername as Sender FROM Nachrichten LEFT JOIN Accounts ON Nachrichten.Empfaenger = Accounts.ID LEFT JOIN Accounts as Accounts_2 On Nachrichten.Sender = Accounts_2.ID WHERE (Accounts_2.Benutzername = ? AND Accounts.Benutzername = ?) OR (Accounts.Benutzername = ? AND Accounts_2.Benutzername = ?)', (current_user.username, button, current_user.username, button))
    rv = wert.fetchall()
    #return redirect(url_for('index2', error = Jsonstr))
    conn.close()
    x = json.dumps(rv)
    return x

@app.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    conn = sqlite3.connect('ChatServer.db')
    conn.row_factory = sqlite3.Row
    wert = conn.cursor()
    button = request.form['Profilseite']
    wert.execute('SELECT * FROM Accounts WHERE Accounts.Benutzername = ?', (button,))
    rv = wert.fetchall()
    return render_template('profil.html', Accountdaten=rv)

@app.route('/saveProfil', methods=['POST'])
@login_required
def saveProfil():
    conn = sqlite3.connect('ChatServer.db')
    conn.row_factory = sqlite3.Row
    wert = conn.cursor()
    file = request.files['file']
    try:
        button = request.form['save']
        if button == 'Speichern':
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                wert.execute('Update Accounts SET Telefonnummer = ?, Status = ?, Geburtstag = ?, Postleitzahl = ?, Stadt = ?, Straße = ?, Hausnummer = ?, Addresszusatz = ?, Vorname = ?, Nachname = ?, EMail = ?, Profilbild = ?  WHERE Accounts.ID = ?', (request.form['Telefonnummer'], request.form['Status'], request.form['Geburtstag'], request.form['Postleitzahl'], request.form['Stadt'], request.form['Straße'], request.form['Hausnummer'], request.form['Addresszusatz'], request.form['Vorname'], request.form['Nachname'], request.form['EMail'], secure_filename(file.filename), request.form['ID']))
            else:
                wert.execute('Update Accounts SET Telefonnummer = ?, Status = ?, Geburtstag = ?, Postleitzahl = ?, Stadt = ?, Straße = ?, Hausnummer = ?, Addresszusatz = ?, Vorname = ?, Nachname = ?, EMail = ? WHERE Accounts.ID = ?', (request.form['Telefonnummer'], request.form['Status'], request.form['Geburtstag'], request.form['Postleitzahl'], request.form['Stadt'], request.form['Straße'], request.form['Hausnummer'], request.form['Addresszusatz'], request.form['Vorname'], request.form['Nachname'], request.form['EMail'], request.form['ID']))
        else:
            wert.execute('SELECT Inhalt, Zeit, Accounts_2.Benutzername as Sender FROM Nachrichten LEFT JOIN Accounts ON Nachrichten.Empfaenger = Accounts.ID LEFT JOIN Accounts as Accounts_2 On Nachrichten.Sender = Accounts_2.ID WHERE (Accounts_2.Benutzername = ? AND Accounts.Benutzername = ?) OR (Accounts.Benutzername = ? AND Accounts_2.Benutzername = ?)', (current_user.username, button, current_user.username, button))
            rv = wert.fetchall()
            conn.close()
            return render_template('forms.html', title='test', error=button, Nachrichten=rv)
    except:
        button = request.form['block']
        wert.execute('Update Contacts Set Blockiert = (Case When Blockiert == 0 then 1 else 0 END) Where Contacts.Benutzername = (Select ID from Accounts where Accounts.Benutzername = ?) AND Contacts.Kontaktname = (Select ID from Accounts where Accounts.Benutzername = ?)', (current_user.username, button))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(ssl_context=(certificate_file, private_key_file), host="0.0.0.0", port=int(8080), debug=True)
    #app.run(debug=True)
