from typing import List
from flask import Flask, render_template, request, redirect, url_for, abort
from models import db, Article, User
from flask_migrate import Migrate
from forms import ArticleForm, LoginForm, RegistrationForm
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
db.app = app
db.init_app(app)
migrate = Migrate(app, db)
Bootstrap(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def homepage():
    articles: List[Article] = Article.query.all()
    return render_template("index.html", title='Главная страница', articles=articles)


@app.route('/articles/search')
def search_article():
    q = request.args.get("q", "")
    articles: List[Article] = Article.query.filter(Article.title.like(f"%{q}%") | Article.body.like(f"%{q}%")).all()
    return render_template("index.html", title='Главная страница', articles=articles)


@app.route('/articles/<int:article_id>')
def get_article(article_id):
    article: Article = Article.query.filter_by(id=article_id).first()
    return render_template('article.html', article=article)


@app.route('/articles/new', methods=["GET", "POST"])
@login_required
def new_article():
    form = ArticleForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        is_verified = form.is_verified.data
        article = Article(title=title, body=body, is_verified=is_verified, user=current_user)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for("get_article", article_id=article.id))
    return render_template("new_article.html", form=form)


@app.route('/articles/<int:article_id>/edit', methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    article: Article = Article.query.filter_by(id=article_id).first()
    form = ArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.body = form.body.data
        article.is_verified = form.is_verified.data
        db.session.add(article)
        db.session.commit()
        return redirect(url_for("get_article", article_id=article.id))
    else:
        form.title.data = article.title
        form.body.data = article.body
        form.is_verified.data = article.is_verified
        return render_template('edit_article.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None or user.check_password(password) == False:
            abort(400)
        login_user(user)
        return redirect(url_for("homepage"))
    return render_template("login.html", form=form)


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route('/registration', methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        existing_user = User.query.filter(User.username.like(username) | User.email.like(email)).first()
        if existing_user is not None:
            abort(400)
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("homepage"))
    return render_template("registration.html", form=form)

@app.errorhandler(401)
def unauthorized(error):
    return render_template("unauthorized.html")



if __name__ == '__main__':
    app.run()
