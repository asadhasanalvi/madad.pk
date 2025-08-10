from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///submissions.db'
app.config['SECRET_KEY'] = 'super-secret-key'
db = SQLAlchemy(app)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
with app.app_context():
    db.create_all()

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get['name']
    service = request.form.get['service']
    other_service = request.form.get('other_service')
    phone = request.form.get['phone']
    email = request.form.get['email']
    address = request.form.get['address']
    details = request.form.get['details']

    final_service = other_service if service == 'Other' else service

    new_submission = Submission(
        name=name,
        service=final_service,
        phone=phone,
        email=email,
        address=address,
        details=details
    )
    db.session.add(new_submission)
    db.session.commit()

    flash("Your request has been submitted successfully.")
    return redirect('/') 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Choose another.', 'error')
            return redirect('/register')
        
        new_user = User(username=username, name=name, phone=phone)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['admin_logged_in'] = True
            session['user_id'] = user.id
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect("/admin")
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        flash('Please log in first.', 'warning')
        return redirect('/login')
    all_data = Submission.query.order_by(Submission.timestamp.desc()).all()
    return render_template('admin.html', submissions=all_data)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

