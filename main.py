from flask import Flask, render_template, redirect, request, make_response
from data import db_session
from data.users import User
from data.news import News
from forms.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/blogs.db")

    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.id > 1, User.email.notilike("%1%")):
        print(user)

    news = News(title="Первая новость", content="Привет блог!",
                user_id=1, is_private=False)
    db_sess.add(news)
    db_sess.commit()

    news = News(title="Вторая новость", content="Привет блог!",
                user_id=2, is_private=False)
    db_sess.add(news)
    db_sess.commit()

    @app.route("/")
    def index():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.is_private != True)
        return render_template("index.html", news=news)

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
                about=form.about.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route("/cookie_test")
    def cookie_test():
        visits_count = int(request.cookies.get("visits_count", 0))
        if visits_count:
            res = make_response(
                f"Вы пришли на эту страницу {visits_count + 1} раз")
            res.set_cookie("visits_count", str(visits_count + 1),
                           max_age=60 * 60 * 24 * 365 * 2)
        else:
            res = make_response(
                "Вы пришли на эту страницу в первый раз за последние 2 года")
            res.set_cookie("visits_count", '1',
                           max_age=60 * 60 * 24 * 365 * 2)
        return res

    app.run()

if __name__ == '__main__':
    main()