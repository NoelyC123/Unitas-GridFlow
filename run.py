from app import create_app

# WSGI entrypoint for flask/gunicorn
app = create_app()

if __name__ == "__main__":
    # dev only
    app.run(host="127.0.0.1", port=5000, debug=True)