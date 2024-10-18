import os
import smtplib
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from forms import LoginForm, CreateProjectForm, RegisterForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
db = SQLAlchemy(model_class=Base)

bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))


class Project(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    subtitle: Mapped[str] = mapped_column(String(250), unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():

    results = db.session.execute(db.select(Project)).fetchmany(6)
    index_projects = [r[0] for r in results]

    return render_template("index.html", all_projects=index_projects)


@app.route("/send_message", methods=["POST"])
def send_message():
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=os.getenv('SMTP_USER'), password=os.getenv('SMTP_PASSWORD'))
        connection.sendmail(from_addr=os.getenv('SMTP_USER'), to_addrs=os.getenv('SMTP_USER'),
                      msg=f"Subject:Contato Via Portfolio\n\nFrom {request.form['name']} - {request.form['email']}\n{request.form['message']}")
        connection.close()
    return redirect(url_for('index'))


@app.route("/aboutme")
def about_me():
    return render_template("aboutme.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    loginform = LoginForm()

    if not loginform.validate_on_submit():
        return render_template('login.html', form=loginform)

    result = db.session.execute(db.select(User).where(User.email == loginform.email.data))
    user = result.scalar()

    if not user:
        return render_template('login.html', form=loginform)

    if not check_password_hash(user.password, loginform.password.data):
        return render_template('login.html', form=loginform)

    if not login_user(user):
        return render_template('login.html', form=loginform)

    return redirect(url_for('index'))


@app.route('/register', methods=["GET", "POST"])
def register():
    registerform = RegisterForm()
    if registerform.validate_on_submit():
        secure_password = generate_password_hash(registerform.password.data, method="pbkdf2:sha256", salt_length=8)

        result = db.session.execute(db.select(User).where(User.email == registerform.email.data))
        user = result.scalar()

        if user:
            return redirect(url_for('login'))

        new_user = User(
            email=registerform.email.data,
            password=secure_password
        )

        db.session.add(new_user)
        db.session.commit()

        db.session.refresh(new_user)

        login_user(new_user)

        return redirect(url_for('index'))

    return render_template('register.html', form=registerform)


@app.route("/create_project", methods=["GET", "POST"])
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        project = Project()
        project.title = form.title.data
        project.subtitle = form.subtitle.data
        project.img_url = form.img_url.data
        project.description = form.description.data

        db.session.add(project)
        db.session.commit()
        return redirect(url_for("project", project_id=project.id))

    return render_template("create_project.html", form=form)


@app.route("/project/<int:project_id>")
def project(project_id):
    actual_project = db.session.execute(db.select(Project).where(Project.id == project_id)).scalar()
    return render_template("project.html", project_loaded=actual_project)


@app.route("/edit_project/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    project = db.session.execute(db.select(Project).where(Project.id == project_id)).scalar()

    edit_form = CreateProjectForm(
        title=project.title,
        subtitle=project.subtitle,
        img_url=project.img_url,
        description=project.description
    )

    if edit_form.validate_on_submit():
        project.title = edit_form.title.data
        project.subtitle = edit_form.subtitle.data
        project.img_url = edit_form.img_url.data
        project.description = edit_form.description.data
        db.session.commit()
        return redirect(url_for("project", project_id=project.id))
    return render_template("create_project.html", form=edit_form, is_edit=True)


@app.route("/delete_project/<int:project_id>")
def delete_project(project_id):
    project_to_delete = db.session.execute(db.select(Project).where(Project.id == project_id)).scalar()
    db.session.delete(project_to_delete)
    db.session.commit()
    return redirect(url_for('portfolio'))


@app.route("/portfolio")
def portfolio():
    results = db.session.execute(db.select(Project)).fetchall()
    all_projects = [r[0] for r in results]
    return render_template("portfolio.html", logged_in=current_user.is_authenticated, all_projects=all_projects)


if __name__ == '__main__':
    app.run(debug=True)
