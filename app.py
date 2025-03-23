from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Authentication middleware
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({
            'status': 'success',
            'message': 'Login successful'
        })
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid email or password'
    }), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Validate input
    if not all([data.get('fullname'), data.get('email'), data.get('password')]):
        return jsonify({
            'status': 'error',
            'message': 'All fields are required'
        }), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'status': 'error',
            'message': 'Email already registered'
        }), 400

    new_user = User(
        fullname=data['fullname'],
        email=data['email'],
        password=generate_password_hash(data['password'])
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Account created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error creating account'
        }), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/favorites', methods=['GET', 'POST'])
@login_required
def favorites():
    if request.method == 'GET':
        user_favorites = Favorite.query.filter_by(user_id=session['user_id']).all()
        return render_template('favorites.html', favorites=user_favorites)
    
    # Handle adding new favorite
    data = request.json
    new_favorite = Favorite(
        image_path=data['image_path'],
        title=data.get('title', ''),
        tags=data.get('tags', ''),
        user_id=session['user_id']
    )
    
    try:
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Added to favorites'})
    except:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to add favorite'}), 500

if __name__ == '__main__':
    app.run(debug=True) 