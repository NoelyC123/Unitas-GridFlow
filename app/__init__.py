import os

from flask import Flask, jsonify, render_template


def create_app() -> Flask:
    base_dir = os.path.dirname(os.path.abspath(__file__))

    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, "static"),
        template_folder=os.path.join(base_dir, "templates"),
    )

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "unitas-gridflow-dev-key")

    @app.get("/health/full")
    def health_full():
        return jsonify(
            {
                "ok": True,
                "service": "unitas-gridflow",
                "version": "dev",
                "status": "healthy",
            }
        )

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/upload")
    def upload():
        return render_template("upload.html")

    try:
        from app.routes.jobs_page import jobs_bp

        app.register_blueprint(jobs_bp, url_prefix="/jobs")
    except Exception as exc:
        app.logger.warning(f"jobs_page blueprint not loaded: {exc}")

    try:
        from app.routes.api_rulepacks import api_rulepacks_bp

        app.register_blueprint(api_rulepacks_bp, url_prefix="/api/rulepacks")
    except Exception as exc:
        app.logger.warning(f"api_rulepacks blueprint not loaded: {exc}")

    try:
        from app.routes.api_upload import api_upload_bp

        app.register_blueprint(api_upload_bp, url_prefix="/api")
    except Exception as exc:
        app.logger.warning(f"api_upload blueprint not loaded: {exc}")

    try:
        from app.routes.api_jobs import api_jobs_bp

        app.register_blueprint(api_jobs_bp, url_prefix="/api/jobs")
    except Exception as exc:
        app.logger.warning(f"api_jobs blueprint not loaded: {exc}")

    try:
        from app.routes.api_intake import api_intake_bp

        app.register_blueprint(api_intake_bp, url_prefix="/api")
    except Exception as exc:
        app.logger.warning(f"api_intake blueprint not loaded: {exc}")

    try:
        from app.routes.map_preview import map_preview_bp

        app.register_blueprint(map_preview_bp, url_prefix="/map")
    except Exception as exc:
        app.logger.warning(f"map_preview blueprint not loaded: {exc}")

    try:
        from app.routes.pdf_reports import pdf_reports_bp

        app.register_blueprint(pdf_reports_bp, url_prefix="/pdf")
    except Exception as exc:
        app.logger.warning(f"pdf_reports blueprint not loaded: {exc}")

    return app
