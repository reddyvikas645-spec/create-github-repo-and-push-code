import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from frontend.backend.app import app


class VercelPathMiddleware:
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        path_info = environ.get("PATH_INFO", "/")
        function_prefix = "/api/index"

        if path_info == function_prefix:
            environ["PATH_INFO"] = "/"
        elif path_info.startswith(f"{function_prefix}/"):
            environ["PATH_INFO"] = path_info[len(function_prefix):]

        return self.application(environ, start_response)


app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
