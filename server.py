from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy, session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, Float, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError
import sqlite3
import datetime
import os
from dotenv import load_dotenv

load_dotenv()


# get the current year for Copyright
def get_year():
    data = datetime.datetime.now()
    return data.year


# keep count of tasks
def counts(item):
    counter = [0, 0]
    for task in item:
        if task.status == 'Incomplete':
            counter[0] += 1
        if task.status == 'Completed':
            counter[1] += 1
    return counter


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap5(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
# initialize the app with the extension
db.init_app(app)
# form select options
status_options = [('Incomplete', 'Incomplete'), ('Completed', 'Completed')]
edit_status_options = [('Incomplete', 'Incomplete'), ('Completed', 'Completed'), ('DELETE', 'DELETE')]


# setup db
class ToDo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False)


class AddToDo(FlaskForm):
    task = StringField('Task to be added:', validators=[DataRequired(), Length(min=5)])
    status = SelectField('Completion Status', choices=status_options)
    add = SubmitField('Add')


class EditStatus(FlaskForm):
    status = SelectField('Current Status', choices=edit_status_options)
    add = SubmitField('Update')


# create db if it does not exist
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    result = db.session.execute(db.select(ToDo).order_by(ToDo.id))
    todo = result.scalars()
    item_count = counts(todo)
    result = db.session.execute(db.select(ToDo).order_by(ToDo.id))
    todo = result.scalars()
    return render_template('index.html', todo=todo, year=get_year(), items=item_count)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddToDo()
    if request.method == 'POST':
        task_to_add = ToDo(
            task=request.form['task'].title(),
            status=request.form['status'],
        )
        db.session.add(task_to_add)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add.html', form=form, year=get_year())


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditStatus()
    if request.method == 'POST':
        task_id = request.args.get('id')
        task = db.session.execute(db.select(ToDo).where(ToDo.id == task_id)).scalar()
        if request.form['status'] == 'Incomplete':
            print('false')
        task.status = request.form['status']
        db.session.commit()
        return redirect(url_for('home'))

    task_id = request.args.get('id')
    task = db.session.execute(db.select(ToDo).where(ToDo.id == task_id)).scalar()
    return render_template('edit_status.html', form=form, task=task, year=get_year())


if __name__ == '__main__':
    app.run(debug=False)
