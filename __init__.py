from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from app.routes import main
    app.register_blueprint(main)

    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    return app