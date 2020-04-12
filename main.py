import datetime
import os
from config import LOGIN, PASSWORD
import requests
from flask import Flask, render_template, url_for, request
from flask_restful import reqparse, abort, Api, Resource
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from werkzeug.utils import redirect, secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, FileField, \
    SelectField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import user
from data import genre
from data import news
from data import reviews
import vk_api
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/users.db")
data = {'ru': {'reg': 'Регистрация', 'ent': 'Войти', 'abo': 'О нас', 'libot': 'Список ботов',
               'parea': 'Личный кабинет', 'exi': 'Выйти', "lwor": "Последние работы",
               'ide': "В разработке",
               "text_abo": "Этот проект создан учениками Яндекс лицей из города Саратова(Гаранин Дмитрий, Астафуров Данил), главной спецификации проекта стало проектирование различных ботов в вк с различными возможностями, в данные момент идет активное программирование ботов.",
               "auto": "Авторизация", 'fname': 'Имя:', 'lname': 'Фамилия:', 'vk': 'Ссылка на вк:',
               'age': 'Возраст:', 'gen': 'Пол:', 'data': 'Дата регистрации:', 'reviews': 'Отзывы',
               'add_work': 'Добавить работу', 'change': 'Изменить', "delete": 'Удалить',
               'specialization': 'специализация'},
        'en': {'reg': 'Registration', 'ent': 'Log in', 'abo': 'About us', 'libot': 'List bots',
               'parea': 'My profile', 'exi': 'Log out', "lwor": "Last works",
               "ide": "In developing",
               "text_abo": "This project was created by students of Yandex Lyceum from the city of Saratov (Dmitry Garanin, Danil Astafurov), the main specification of the project was the design of various bots in VK with various capabilities, at the moment there is active programming of bots.",
               "auto": "Authorizarion", 'fname': 'Name:', 'lname': 'Surname:', 'vk': 'Vk_url:',
               'age': 'Age:', 'gen': 'Gender:', 'data': 'Registration date:', 'reviews': 'Reviews',
               'add_work': 'Add job', 'change': 'Edit', "delete": 'Delete',
               'specialization': 'specialization'}}
lang = "ru"
now = "/"


def change_now(data):
    global now
    now = data


def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


class RegisterForm(FlaskForm):
    Email = StringField('Email', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Password_again = PasswordField('Repeat password', validators=[DataRequired()])
    Surname = StringField('Surname', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Age = StringField('Age', validators=[DataRequired()])
    Vk_url = StringField('Vk_url', validators=[DataRequired()])
    Gender = RadioField('Gender', choices=[
        ("Female", 'Female'), ('Male', 'Male')],
                        default=1, coerce=str)
    submit = SubmitField('Sumbit')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class EditForm(FlaskForm):
    Surname = StringField('Surname', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Age = StringField('Age', validators=[DataRequired()])
    Vk_url = StringField('Vk_url', validators=[DataRequired()])
    Gender = RadioField('Gender', choices=[
        ("Female", 'Female'), ('Male', 'Male')],
                        default=1, coerce=str)
    submit = SubmitField('Sumbit')


class NewsForm(FlaskForm):
    Bot_title = StringField('Title', validators=[DataRequired()])
    Genre = StringField('Genre', validators=[DataRequired()])
    photo = FileField(validators=[FileRequired()])
    submit = SubmitField('Sumbit')


class Add_Reviewsform(FlaskForm):
    session = db_session.create_session()
    bot = SelectField('Бот', choices=[
        *[(user.name_bot, user.name_bot) for user in session.query(news.News).all()]])
    text = TextAreaField("Текст")
    submit = SubmitField('Sumbit')


class Change_bot(FlaskForm):
    session = db_session.create_session()
    bot = SelectField('Бот', choices=[
        *[(user.name_bot, user.name_bot) for user in session.query(news.News).all()]])
    submit = SubmitField('Sumbit')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/ru')
def ruf():
    global lang
    lang = "ru"
    return redirect(now)


@app.route('/en')
def enf():
    global lang
    lang = "en"
    return redirect(now)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(user.User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def main():
    change_now('/')
    session = db_session.create_session()
    news1 = session.query(news.News).all()
    for i in news1:
        f = open(f"static\img\inews_tmp\img{i.id}.png", mode="wb")
        f.write(i.image)
        f.close()
    return render_template('main.html', title="2DYES", data=data, lang=lang, user_list=news1)


@app.route('/about_us', methods=['GET', 'POST'])
def about_usf():
    change_now('/about_us')
    return render_template('about_us.html', title="2DYES", data=data, lang=lang)


@app.route('/list_bot', methods=['GET', 'POST'])
def list_botf():
    change_now('/list_bot')
    session = db_session.create_session()
    news1 = session.query(news.News).all()
    return render_template('list_bot.html', title="2DYES", data=data, lang=lang, user_list=news1)


@app.route('/my_profile', methods=['GET', 'POST'])
def my_profilef():
    change_now('/my_profile')
    login, password = LOGIN, PASSWORD
    vk_session = vk_api.VkApi(
        login, password,
        auth_handler=auth_handler
    )
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk = vk_session.get_api()
    dataa = requests.get(
        vk.users.get(user_ids=f"{current_user.vk_url.split('/')[-1]}", fields="photo_400_orig")[0][
            'photo_400_orig'])
    out = open(f"static/img/tmp/img{current_user.id}.jpg", "wb")
    out.write(dataa.content)
    out.close()
    return render_template('my_profile.html', title="2DYES", data=data, lang=lang,
                           current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    change_now('/register')
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
            vk_url=form.Vk_url.data,
            data_reg=datetime.datetime.now()
        )
        user1.set_password(form.Password.data)
        session.add(user1)
        session.commit()
        return redirect(url_for("main"))
    return render_template('register.html', title='Регистрация', form=form, data=data, lang=lang)


@app.route('/login', methods=['GET', 'POST'])
def login():
    change_now('/login')
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


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    change_now('/news')
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        newss = news.News()
        genree = genre.Genre()
        genree.name = form.Genre.data
        newss.name_bot = form.Bot_title.data
        newss.genre.append(genree)
        newss.image = form.photo.data.read()
        current_user.newss.append(newss)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление работы',
                           form=form, data=data, lang=lang)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    change_now(f'/news/{id}')
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(news.News).filter(news.News.id == id,
                                              current_user.id == 1).first()
        if job:
            job.name_bot = form.Bot_title.data
            job.image = form.photo.data
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(news.News).filter(news.News.id == id,
                                              (news.News.user == current_user) | (
                                                      current_user.id == 1)).first()
        if job:
            genree = genre.Genre()
            genree.name = form.Genre.data
            job.name_bot = form.Bot_title.data
            job.image = form.photo.data.read()
            job.genre.remove(job.genre[0])
            job.genre.append(genree)
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование работы', form=form, data=data,
                           lang=lang)


@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    change_now(f'/user/{id}')
    form = EditForm()
    if request.method == "GET":
        session = db_session.create_session()
        users = session.query(user.User).filter(user.User.id == id,
                                                current_user.id == id).first()
        if users:
            users.email = users.email
            users.hashed_password = users.hashed_password
            users.surname = users.surname
            users.name = users.name
            users.age = users.age
            users.gender = users.gender
            users.vk_url = users.vk_url
            users.data_reg = users.data_reg
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        users = session.query(user.User).filter(user.User.id == id, current_user.id == id).first()
        if users:
            users.surname = form.Surname.data
            users.name = form.Name.data
            users.age = form.Age.data
            users.gender = form.Gender.data
            users.vk_url = form.Vk_url.data
            session.commit()
            return redirect('/my_profile')
        else:
            abort(404)
    return render_template('useredit.html', title='Редактирование работы', form=form, data=data,
                           lang=lang)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    change_now(f'/news_delete/{id}')
    session = db_session.create_session()
    job = session.query(news.News).filter(news.News.id == id, current_user.id == 1).first()
    if job:
        session.delete(job)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/reviews', methods=['GET', 'POST'])
@login_required
def reviews123():
    change_now('/reviews')
    form = Change_bot()
    session = db_session.create_session()
    reviews_data = session.query(reviews.Reviwes).all()
    if form.validate_on_submit():
        reviews_data = session.query(reviews.Reviwes).filter(
            reviews.Reviwes.name_bot == form.bot.data).all()
        return render_template('reviews.html', title='Редактирование работы', data=data,
                               lang=lang, form=form, reviews_data=reviews_data)
    return render_template('reviews.html', title='Редактирование работы', data=data,
                           lang=lang, form=form, reviews_data=reviews_data)


@app.route('/reviews_add', methods=['GET', 'POST'])
@login_required
def reviews_addf():
    change_now('/reviews_add')
    form = Add_Reviewsform()
    if form.validate_on_submit():
        session = db_session.create_session()
        riew = reviews.Reviwes()
        riew.text = form.text.data
        riew.name_bot = form.bot.data
        current_user.reviewss.append(riew)
        session.merge(current_user)
        session.commit()
        return redirect('/reviews')
    return render_template('add_reviews.html', title='Добавление работы',
                           form=form, data=data, lang=lang)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
