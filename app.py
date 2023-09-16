from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    #thematic = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def validate_credentials(username, password):
    user = user.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return True
    return False
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_username = request.form['username']
        entered_password = request.form['password']

        if validate_credentials(entered_username, entered_password):
            session['user_name'] = entered_username
            flash('Login succesful', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Authentication failed', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        #thematic = request.form['thematic']
        # Add more fields from the registration form

        # Check if the email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email address is already registered', 'danger')
            return redirect(url_for('register'))

        # Create a new user and store in the database
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin')
def admin():
    if 'user_name' in session:
        user_name = session['user_name']
        return render_template('admin.html', user_name=user_name)
    
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    flash('Logout successful', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)