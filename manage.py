from flask import Flask
from flask_migrate import Migrate
from app import create_app, db



# Crear la aplicación Flask
app = create_app()

# Inicializar Flask-Migrate
migrate = Migrate(app, db)

# Crear tablas en caso de que no existan
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
