from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.models import User, Favorite, Upload, db
from werkzeug.urls import url_parse
import os
import jwt
from datetime import datetime, timedelta

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
@main.route('/home')
@login_required
def home():
    return render_template('index.html')

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, current_app.config['SECRET_KEY'])

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'redirect': '/upload'
        })
    
    return jsonify({
        'status': 'error',
        'message': 'Invalid email or password'
    }), 401

@auth.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({
            'status': 'error',
            'message': 'Email already registered'
        }), 400

    user = User(
        username=data.get('username'),
        email=data.get('email')
    )
    user.set_password(data.get('password'))

    try:
        db.session.add(user)
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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@main.route('/favorites')
@login_required
def favorites():
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=user_favorites)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            upload = Upload(filename=filename, user_id=current_user.id)
            db.session.add(upload)
            db.session.commit()
            
            return jsonify({'success': True, 'filename': filename})
            
        return jsonify({'success': False, 'message': 'File type not allowed'}), 400
        
    return render_template('upload.html') 