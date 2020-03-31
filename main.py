import datetime

from flask import Flask, render_template, url_for
from flask_login import LoginManager, login_required, logout_user, login_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import user

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/users.db")
data = {'ru': {'reg': 'Регистрация', 'ent': 'Войти', 'abo': 'О нас', 'libot': 'Список ботов',
               'parea': 'Личный кабинет', 'exi': 'Выйти'},
        'en': {'reg': 'Registration', 'ent': 'Log in', 'abo': 'About us', 'libot': 'List bots',
               'parea': 'My profile', 'exi': 'Log out'}}
lang = "ru"


class RegisterForm(FlaskForm):
    Email = StringField('Email', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Password_again = PasswordField('Repeat password', validators=[DataRequired()])
    Surname = StringField('Surname', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Age = StringField('Age', validators=[DataRequired()])
    Gender = RadioField('Gender', choices=[
        ("Female", 'Female'), ('Male', 'Male')],
                        default=1, coerce=str)
    submit = SubmitField('Sumbit')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/ru')
def ruf():
    global lang
    lang = "ru"
    return redirect("/")


@app.route('/en')
def enf():
    global lang
    lang = "en"
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(user.User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html', title="2DYES", data=data, lang=lang)


@app.route('/about_us', methods=['GET', 'POST'])
def about_usf():
    return render_template('about_us.html', title="2DYES", data=data, lang=lang)


@app.route('/list_bot', methods=['GET', 'POST'])
def list_botf():
    return render_template('list_bot.html', title="2DYES", data=data, lang=lang)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.Password.data != form.Password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", data=data, lang=lang)
        session = db_session.create_session()
        if session.query(user.User).filter(user.User.email == form.Email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", data=data, lang=lang)
        user1 = user.User(
            email=form.Email.data,
            surname=form.Surname.data,
            name=form.Name.data,
            age=form.Age.data,
            gender=form.Gender.data,
            data_reg=datetime.datetime.now()
        )
        user1.set_password(form.Password.data)
        session.add(user1)
        session.commit()
        return redirect(url_for("main"))
    return render_template('register.html', title='Регистрация', form=form, data=data, lang=lang)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user1 = session.query(user.User).filter(user.User.email == form.email.data).first()
        if user1 and user1.check_password(form.password.data):
            login_user(user1, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, data=data, lang=lang)
    return render_template('login.html', title='Авторизация', form=form, data=data, lang=lang)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
