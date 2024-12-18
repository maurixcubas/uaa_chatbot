from flask import Blueprint, request, jsonify, session, redirect, url_for, send_file
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        return {"success": False, "message": "User already exists"}, 409

    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone']
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return {"success": True, "message": "User registered successfully"}

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        session['username'] = user.email
        return {"success": True, "message": "Login successful"}
    return {"success": False, "message": "Invalid credentials"}, 401

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.home'))

@auth_bp.route('/home')
def home():
    return {"success": True, "message": "Welcome to the home page!"}
    
@auth_bp.route('/download-db', methods=['GET'])
def download_db():
    try:
        # Ruta relativa al archivo dentro de tu proyecto
        db_path = "instance/combined.db"
        return send_file(db_path, as_attachment=True)
    except Exception as e:
        return {"success": False, "message": str(e)}, 500
