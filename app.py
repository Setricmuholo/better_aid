from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import openai
from datetime import datetime

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

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Add authentication logic

        flash('Login succesful', 'success')
        return redirect(url_for('index.html'))
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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    flash('Logout successful', 'success')
    return redirect(url_for('login'))

@app.route('/research')
def research():
    return render_template('research.html')

# Function to send user message to ChatGPT
def send_message_to_chatgpt(message):
    # Set your OpenAI API key here
    api_key = "s"

    # Initialize the OpenAI API client with your API key
    openai.api_key = api_key

    # Define the user's message as the prompt
    prompt = message

    # Use the OpenAI API to generate a response
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",  # Adjust the engine as needed
            prompt=prompt,
            max_tokens=50,           # Adjust for desired response length
        )

        # Extract the AI's response text from the API response
        ai_response = response.choices[0].text.strip()
        
        return ai_response
    except Exception as e:
        # Handle API request errors
        return f'Error: {str(e)}'

# Route to render the chat page
@app.route('/chat')
def chat():
    return render_template('chat.html')

# Route to handle user messages and send AI responses
@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form.get('user_message')
    
    # Send the user's message to ChatGPT and receive a response
    ai_response = send_message_to_chatgpt(user_message)

    # Return the AI's response as JSON
    return jsonify({'response': ai_response})

@app.route('/test_api_request')
def test_api_request():
    test_message = "Hello, ChatGPT!"
    response = send_message_to_chatgpt(test_message)
    print(response)  # Print the response to your server console
    return response

@app.route('/work', methods=['POST', 'GET'])
def work():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/work')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('work.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/work')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/work')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)