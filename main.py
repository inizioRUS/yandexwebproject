import datetime
import os
from config import secret_key, key1, key2
from flask import Flask, render_template, request
from flask_restful import abort, Api
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileRequired
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, FileField, \
    SelectField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data.user import User
from data.genre import Genre
from data.news import News
from data.reviews import Reviwes
from data import db_session
from data.reviewsr import ReviewListResource, ReviewResource
from data.userr import UserListResource, UserResource
from data.newsr import NewsListResource, NewsResource

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = secret_key
app.config['RECAPTCHA_PUBLIC_KEY'] = key1
app.config['RECAPTCHA_PRIVATE_KEY'] = key2
login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/users.db")

translate = {'ru': {'reg': 'Регистрация', 'ent': 'Войти', 'abo': 'О нас', 'libot': 'Список ботов',
                    'parea': 'Личный кабинет', 'exi': 'Выйти', "lwor": "Последние работы",
                    'ide': "В разработке", "add_review": "Добавить отзыв",
                    "text_abo": "Этот проект создан учениками Яндекс лицей из города Саратова(Гаранин Дмитрий, Астафуров Данил), главной спецификации проекта стало проектирование различных ботов в вк с различными возможностями, в данные момент идет активное программирование ботов.",
                    "auto": "Авторизация", 'fname': 'Имя:', 'lname': 'Фамилия:',
                    'cont': 'Способ контакта:',
                    'login': 'Логин:', 'gen': 'Пол:', 'data': 'Дата регистрации:',
                    'reviews': 'Отзывы',
                    'add_work': 'Добавить работу', 'change': 'Изменить', "delete": 'Удалить',
                    'specialization': 'специализация', 'name_bot': 'Название бота:',
                    'user': 'Пользователь:', 'review_text': "Текст отзыва:"},
             'en': {'reg': 'Registration', 'ent': 'Log in', 'abo': 'About us', 'libot': 'List bots',
                    'parea': 'My profile', 'exi': 'Log out', "lwor": "Last works",
                    "ide": "In developing", "add_review": "Add a review",
                    "text_abo": "This project was created by students of Yandex Lyceum from the city of Saratov (Dmitry Garanin, Danil Astafurov), the main specification of the project was the design of various bots in VK with various capabilities, at the moment there is active programming of bots.",
                    "auto": "Authorizarion", 'fname': 'Name:', 'lname': 'Surname:',
                    'cont': 'Contact:',
                    'login': 'Login:', 'gen': 'Gender:', 'data': 'Registration date:',
                    'reviews': 'Reviews',
                    'add_work': 'Add job', 'change': 'Edit', "delete": 'Delete',
                    'specialization': 'specialization', 'name_bot': 'Bot name:', 'user': 'User:',
                    'review_text': "Review text:"}}
now_page = "/"
lang = "en"


def change_lang():
    global lang
    try:
        return current_user.lang
    except Exception:
        return lang


def change_now(data):
    global now_page
    now_page = data


class RegisterForm(FlaskForm):
    Email = StringField('Email', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    Password_again = PasswordField('Repeat password', validators=[DataRequired()])
    Surname = StringField('Surname', validators=[DataRequired()])
    Login = StringField('Login', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Contact = StringField('Contact', validators=[DataRequired()])
    Gender = RadioField('Gender', choices=[
        ("Female", 'Female'), ('Male', 'Male')],
                        default=1, coerce=str)
    photo = FileField(validators=[FileRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class EditForm(FlaskForm):
    Surname = StringField('Login', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Login = StringField('Surname', validators=[DataRequired()])
    Contact = StringField('Contact', validators=[DataRequired()])
    Gender = RadioField('Gender', choices=[
        ("Female", 'Female'), ('Male', 'Male')],
                        default=1, coerce=str)
    photo = FileField(validators=[FileRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')


class NewsForm(FlaskForm):
    Bot_title = StringField('Title', validators=[DataRequired()])
    Genre = StringField('Genre', validators=[DataRequired()])
    Url = StringField('Url', validators=[DataRequired()])
    photo = FileField(validators=[FileRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')


class Add_Reviewsform(FlaskForm):
    session = db_session.create_session()
    bot = SelectField('Bot', choices=[
        *[(user.name_bot, user.name_bot) for user in session.query(News).all()]])
    text = TextAreaField("Text")
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')


class Add_Reviewsfor_one(FlaskForm):
    session = db_session.create_session()
    text = TextAreaField("Text")
    recaptcha = RecaptchaField()
    submit = SubmitField('Sumbit')


class Change_bot(FlaskForm):
    session = db_session.create_session()
    bot = SelectField('Bot', choices=[
        *[(user.name_bot, user.name_bot) for user in session.query(News).all()]])
    submit = SubmitField('Sumbit')


class Change_Reviewsform(FlaskForm):
    text = TextAreaField("Text")
    submit = SubmitField('Sumbit')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/ru')
@login_required
def ruf():
    session = db_session.create_session()
    current_user.lang = "ru"
    session.merge(current_user)
    session.commit()
    return redirect(now_page)


@app.route('/en')
@login_required
def enf():
    session = db_session.create_session()
    current_user.lang = "en"
    session.merge(current_user)
    session.commit()
    return redirect(now_page)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def main_page():
    change_now('/')
    session = db_session.create_session()
    all_news = session.query(News).all()
    return render_template('main.html', title="2DYES", data=translate, lang=change_lang(),
                           user_list=all_news)


@app.route('/about_us', methods=['GET', 'POST'])
def about_us():
    change_now('/about_us')
    return render_template('about_us.html', title=translate[change_lang()]['abo'], data=translate,
                           lang=change_lang())


@app.route('/list_bot', methods=['GET', 'POST'])
def list_bot():
    change_now('/list_bot')
    session = db_session.create_session()
    all_news = session.query(News).all()
    return render_template('list_bot.html', title=translate[change_lang()]['libot'], data=translate,
                           lang=change_lang(),
                           user_list=all_news)


@app.route('/my_profile', methods=['GET', 'POST'])
def my_profile():
    change_now('/my_profile')
    return render_template('my_profile.html', title=translate[change_lang()]['parea'],
                           data=translate,
                           lang=change_lang(),
                           current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    change_now('/register')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.Password.data != form.Password_again.data:
            return render_template('register.html', title=translate[change_lang()]['reg'],
                                   form=form,
                                   message="Пароли не совпадают", data=translate, lang=change_lang())
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.Email.data).first():
            return render_template('register.html', title=translate[change_lang()]['reg'],
                                   form=form,
                                   message="Такой пользователь уже есть", data=translate,
                                   lang=change_lang())
        user = User(
            email=form.Email.data,
            login=form.Login.data,
            surname=form.Surname.data,
            name=form.Name.data,
            gender=form.Gender.data,
            contact=form.Contact.data,
            image=form.photo.data.read(),
            lang="en",
            id_foto=len([f for f in os.listdir("static/img/tmp")]),
            data_reg=datetime.datetime.now()
        )
        out = open(f"static/img/tmp/{user.id_foto}.jpg", "wb")
        out.write(user.image)
        out.close()
        user.set_password(form.Password.data)
        session.add(user)
        session.commit()
        return redirect("/")
    return render_template('register.html', title=translate[change_lang()]['reg'], form=form,
                           data=translate,
                           lang=change_lang())


@app.route('/login', methods=['GET', 'POST'])
def login():
    change_now('/login')
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, data=translate, lang=change_lang())
    return render_template('login.html', title=translate[change_lang()]['auto'], form=form,
                           data=translate,
                           lang=change_lang())


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    change_now('/news')
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        genre = Genre()
        genre.name = form.Genre.data
        news.name_bot = form.Bot_title.data
        news.genre.append(genre)
        news.image = form.photo.data.read()
        news.url = form.Url.data
        news.foto_id = len([f for f in os.listdir("static/img/inews_tmp")])
        out = open(f"static/img/inews_tmp/{news.foto_id}.jpg", "wb")
        out.write(news.image)
        out.close()
        current_user.newss.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title=translate[change_lang()]['add_work'],
                           form=form, data=translate, lang=change_lang())


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    change_now(f'/news/{id}')
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          current_user.id == 1).first()
        if news:
            news.name_bot = news.name_bot
            news.image = news.image
            news.foto_id = news.foto_id
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          (News.user == current_user) | (
                                                  current_user.id == 1)).first()
        if news:
            genre = Genre()
            genre.name = form.Genre.data
            news.name_bot = form.Bot_title.data
            news.image = form.photo.data.read()
            news.foto_id = len([f for f in os.listdir("static/img/inews_tmp")])
            out = open(f"static/img/inews_tmp/{news.foto_id}.jpg", "wb")
            out.write(news.image)
            out.close()
            news.genre.remove(news.genre[0])
            news.genre.append(genre)
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title=translate[change_lang()]['change'], form=form,
                           data=translate,
                           lang=change_lang())


@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    change_now(f'/user/{id}')
    form = EditForm()
    if request.method == "GET":
        session = db_session.create_session()
        user = session.query(User).filter(User.id == id,
                                          current_user.id == id).first()
        if user:
            user.email = user.email
            user.login = user.login
            user.hashed_password = user.hashed_password
            user.surname = user.surname
            user.gender = user.gender
            user.name = user.name
            user.image = user.image
            user.id_foto = user.id_foto
            user.contact = user.contact
            user.data_reg = user.data_reg
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.id == id, current_user.id == id).first()
        if user:
            user.surname = form.Surname.data
            user.name = form.Name.data
            user.gender = form.Gender.data
            user.contact = form.Contact.data
            user.login = form.Login.data
            user.id_foto = len([f for f in os.listdir("static/img/tmp")])
            user.image = form.photo.data.read()
            out = open(f"static/img/tmp/{user.id_foto}.jpg", "wb")

            out.write(user.image)
            out.close()
            session.commit()
            return redirect('/my_profile')
        else:
            abort(404)
    return render_template('useredit.html', title=translate[change_lang()]['change'], form=form,
                           data=translate,
                           lang=change_lang())


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    change_now(f'/news_delete/{id}')
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id, current_user.id == 1).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/reviews', methods=['GET', 'POST'])
@login_required
def reviewsf():
    change_now('/reviews')
    form = Change_bot()
    session = db_session.create_session()
    reviews_data = session.query(Reviwes).all()
    if form.validate_on_submit():
        reviews_data = session.query(Reviwes).filter(
            Reviwes.name_bot == form.bot.data).all()
        return render_template('reviews.html', title=translate[change_lang()]['reviews'],
                               data=translate,
                               lang=change_lang(), form=form, reviews_data=reviews_data)
    return render_template('reviews.html', title=translate[change_lang()]['reviews'], data=translate,
                           lang=change_lang(), form=form, reviews_data=reviews_data)


@app.route('/reviews_add', methods=['GET', 'POST'])
@login_required
def reviews_addf():
    change_now('/reviews_add')
    form = Add_Reviewsform()
    if form.validate_on_submit():
        session = db_session.create_session()
        riew = Reviwes()
        riew.text = form.text.data
        riew.name_bot = form.bot.data
        current_user.reviewss.append(riew)
        session.merge(current_user)
        session.commit()
        return redirect('/reviews')
    return render_template('add_reviews.html', title=translate[change_lang()]['add_review'],
                           form=form, data=translate, lang=change_lang())


@app.route('/reviews_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def reviews_delete(id):
    change_now(f'/reviews_delete/{id}')
    session = db_session.create_session()
    reviewss = session.query(Reviwes).filter(Reviwes.id == id,
                                             current_user.id == 1).first()
    if reviewss:
        session.delete(reviewss)
        session.commit()
    else:
        abort(404)
    return redirect('/reviews')


@app.route('/reviews/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_use(id):
    change_now(f'/reviews/{id}')
    form = Change_Reviewsform()
    if request.method == "GET":
        session = db_session.create_session()
        reviewss = session.query(Reviwes).filter(Reviwes.id == id ,
                                                 current_user.id == 1).first()
        if reviewss:
            reviewss.id = reviewss.id
            reviewss.user_id = reviewss.user_id
            reviewss.text = reviewss.text
            reviewss.name_bot = reviewss.name_bot
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        reviewss = session.query(Reviwes).filter(Reviwes.id == id,
                                                 current_user.id == 1).first()
        if reviewss:
            reviewss.text = form.text.data
            session.commit()
            return redirect('/reviews')
        else:
            abort(404)
    return render_template('change_reviews.html', title=translate[change_lang()]['change'],
                           form=form,
                           data=translate,
                           lang=change_lang())


@app.route('/reviews_add_one/<int:id>', methods=['GET', 'POST'])
@login_required
def reviews_add_for_onef(id):
    change_now(f'/reviews_add_one/{id}')
    form = Add_Reviewsfor_one()
    if form.validate_on_submit():
        session = db_session.create_session()
        riew = Reviwes()
        riew.text = form.text.data
        riew.name_bot = session.query(News).filter(News.id == id).first().name_bot
        current_user.reviewss.append(riew)
        session.merge(current_user)
        session.commit()
        return redirect('/reviews')
    return render_template('add_reviews_for_one.html', title=translate[change_lang()]['add_review'],
                           form=form, data=translate, lang=change_lang())


api.add_resource(UserListResource, '/api/user')
api.add_resource(UserResource, '/api/user/<int:user_id>')
api.add_resource(NewsListResource, '/api/news')
api.add_resource(NewsResource, '/api/news/<int:news_id>')
api.add_resource(ReviewListResource, '/api/review')
api.add_resource(ReviewResource, '/api/review/<int:rew_id>')
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
