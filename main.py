from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
#connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:m@lik1.4@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fjjMgdDkuo4mFjCDMuCFDatk'

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    task = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()
    return render_template('todos.html', title="Get It Done",
        tasks=tasks, completed_tasks=completed_tasks)

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # mencek terlebih dahulu apakah email bersangkutan sudah ada di database atau belum
        user = User.query.filter_by(email=email).first()
        # checking apakah password email tsb benar spt yg tersimpan di batabase
        if user and user.password == password:
            # TODO - How "REMEMBER" that the user has loggen
            session['email'] = email
            flash('Logged in')
            # print(session)
            return redirect('/')
        else:
            flash('Password is incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            # TODO - "Remember" the user
            session['email'] = email
            return redirect('/')
        else:
            # TODO - User better response messaging
            return '<h1>Duplicate user</h1>'

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run()
