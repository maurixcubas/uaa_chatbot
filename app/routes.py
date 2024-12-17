from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Thread, Message, User
import openai
import uuid
import time
from datetime import datetime
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# ID del asistente configurado previamente
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

api_bp = Blueprint("api", __name__)

# Crear un hilo
@api_bp.route("/threads", methods=["POST"])
def create_thread():
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Buscar el usuario actual
    user = User.query.filter_by(email=session['username']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Crear un nuevo hilo asociado al usuario
    thread_id = str(uuid.uuid4())
    thread = Thread(thread_id=thread_id, user_id=user.id)  # Asocia el hilo al usuario
    db.session.add(thread)
    db.session.commit()

    return jsonify({
        "thread_id": thread.thread_id,
        "created_at": thread.created_at,
        "user_id": user.email
    }), 201

# Enviar mensaje
@api_bp.route("/threads/<string:thread_id>/messages", methods=["POST"])
def send_message(thread_id):
    data = request.json
    if not data or "content" not in data:
        return jsonify({"error": "Content is required"}), 400

    # Buscar el hilo en la base de datos
    thread = Thread.query.filter_by(thread_id=thread_id).first()
    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    # Verificar si el hilo ya tiene un openai_thread_id
    if not thread.openai_thread_id:
        # Si no existe, crear un nuevo hilo en OpenAI
        assistant_thread = openai.beta.threads.create()
        thread.openai_thread_id = assistant_thread.id
        db.session.commit()

    # Obtener el mensaje del usuario y agregarlo a la base de datos
    user_message_time = datetime.utcnow()
    user_message = Message(thread_id=thread.id, role="user", content=data["content"], created_at=user_message_time)
    db.session.add(user_message)
    db.session.commit()

    # Enviar el mensaje al hilo existente en OpenAI
    openai.beta.threads.messages.create(
        thread_id=thread.openai_thread_id,
        role="user",
        content=data["content"]
    )

    # Ejecutar el asistente
    run = openai.beta.threads.runs.create(
        thread_id=thread.openai_thread_id,
        assistant_id="asst_KHN5OaDUdLlGUm8koxaukxKr"
    )

    # Esperar la respuesta del asistente
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread.openai_thread_id, run_id=run.id)
        if run_status.status == "completed":
            break
        time.sleep(1)

    # Obtener el mensaje del asistente
    messages = openai.beta.threads.messages.list(thread_id=thread.openai_thread_id)
    assistant_reply = messages.data[0].content[0].text.value

    # Obtenemos la respuesta del asistente y la agregamos a la base de datos
    assistant_message_time = datetime.utcnow()
    assistant_message = Message(thread_id=thread.id, role="assistant", content=assistant_reply, created_at=assistant_message_time)
    db.session.add(assistant_message)
    db.session.commit()

    return jsonify({
        "user_message": user_message.content,
        "assistant_reply": assistant_message.content,
    }), 201

# Listar hilos
@api_bp.route("/threads", methods=["GET"])
def list_threads():
    if "username" not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Buscar el usuario actual
    user = User.query.filter_by(email=session['username']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Filtrar los hilos asociados al usuario
    threads = Thread.query.filter_by(user_id=user.id).all()
    return jsonify([
        {"thread_id": t.thread_id, "created_at": t.created_at} for t in threads
    ]), 200

# Listar mensajes de un hilo
@api_bp.route("/threads/<string:thread_id>/messages", methods=["GET"])
def list_messages(thread_id):
    thread = Thread.query.filter_by(thread_id=thread_id).first()
    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    messages = Message.query.filter_by(thread_id=thread.id).all()
    return jsonify([
        {"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages
    ]), 200
