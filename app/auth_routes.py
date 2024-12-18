from flask import Blueprint, request, jsonify, session, redirect, url_for, send_file
from app import db
from app.models import User
import os

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
        # Ruta al archivo combinada con la raíz del proyecto
        db_path = os.path.join(os.getcwd(), "instance", "combined.db")
        
        # Verificar si el archivo existe
        if not os.path.exists(db_path):
            return {"success": False, "message": "Archivo no encontrado"}, 404
        
        return send_file(db_path, as_attachment=True)
    except Exception as e:
        return {"success": False, "message": str(e)}, 500

# Borrar un hilo
@api_bp.route("/threads/<string:thread_id>", methods=["DELETE"])
def delete_thread(thread_id):
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Buscar el usuario actual
    user = User.query.filter_by(email=session['username']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Buscar el hilo específico
    thread = Thread.query.filter_by(thread_id=thread_id, user_id=user.id).first()
    if not thread:
        return jsonify({"error": "Thread not found or not authorized"}), 404

    try:
        # Eliminar mensajes asociados al hilo
        Message.query.filter_by(thread_id=thread.id).delete()

        # Eliminar el hilo
        db.session.delete(thread)
        db.session.commit()

        return jsonify({"message": "Thread and associated messages deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete thread: {str(e)}"}), 500
