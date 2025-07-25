from swingmusic import settings
from swingmusic.api import create_api
from swingmusic.crons import start_cron_jobs
from swingmusic.plugins.register import register_plugins
from swingmusic.setup import load_into_mem, run_setup
from swingmusic.start_info_logger import log_startup_info
from swingmusic.utils.filesystem import get_home_res_path
from swingmusic.utils.paths import getClientFilesExtensions
from swingmusic.utils.threading import background
from swingmusic.logger import setup_logger

import pathlib
import setproctitle
from flask import Response, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, set_access_cookies, verify_jwt_in_request

import mimetypes
from datetime import datetime, timezone


def app_builder():

    # Create the Flask app
    app = create_api()
    app.static_folder = get_home_res_path("client")

    # INFO: Routes that don't need authentication
    whitelisted_routes = {
        "/auth/login",
        "/auth/users",
        "/auth/pair",
        "/auth/logout",
        "/auth/refresh",
        "/docs",
    }
    blacklist_extensions = {".webp", ".jpg"}.union(getClientFilesExtensions())

    def skipAuthAction():
        """
        Skips the JWT verification for the current request.
        """
        if request.path == "/" or any(
            request.path.endswith(ext) for ext in blacklist_extensions
        ):
            return True

        # if request path starts with any of the blacklisted routes, don't verify jwt
        if any(request.path.startswith(route) for route in whitelisted_routes):
            return True

        return False

    @app.before_request
    def verify_auth():
        """
        Verifies the JWT token before each request.
        """
        if skipAuthAction():
            return

        verify_jwt_in_request()

    @app.after_request
    def refresh_expiring_jwt(response: Response):
        """
        Refreshes the cookies JWT token after each request.
        """

        # INFO: If the request has an Authorization header, don't refresh the jwt
        # Request is probably from the mobile client or a third party
        if skipAuthAction() or request.headers.get("Authorization"):
            return response

        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now) + 60 * 60 * 24 * 7  # 7 days

            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)

            return response
        except (RuntimeError, KeyError):
            return response

    @app.route("/<path:path>")
    def serve_client_files(path: str):
        """
        Serves the static files in the client folder.
        """

        js_or_css = path.endswith(".js") or path.endswith(".css")

        if not js_or_css:
            return app.send_static_file(path)

        # INFO: Safari doesn't support gzip encoding
        # See issue: https://github.com/swingmx/swingmusic/issues/155
        user_agent = request.headers.get("User-Agent")
        if "Safari" in user_agent and not "Chrome" in user_agent:
            return app.send_static_file(path)

        gzipped_path = pathlib.Path(app.static_folder or "") / path
        gzipped_path = gzipped_path.with_suffix(".gz")

        if "gzip" in request.headers.get("Accept-Encoding", ""):
            if gzipped_path.exists():
                response = app.make_response(app.send_static_file(str(gzipped_path)))
                response.headers["Content-Encoding"] = "gzip"
                return response


        return app.send_static_file(path)


    @app.route("/")
    def serve_client():
        """
        Serves the index.html file at `client/index.html`.
        """
        return app.send_static_file("index.html")

    return app


def config_mimetypes():
    # Load mimetypes for the web client's static files
    # Loading mimetypes should happen automatically but
    # sometimes the mimetypes are not loaded correctly
    # eg. when the Registry is messed up on Windows.

    # See the following issues:
    # https://github.com/swingmx/swingmusic/issues/137

    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("text/javascript", ".js")
    mimetypes.add_type("text/plain", ".txt")
    mimetypes.add_type("text/html", ".html")
    mimetypes.add_type("image/webp", ".webp")
    mimetypes.add_type("image/svg+xml", ".svg")
    mimetypes.add_type("image/png", ".png")
    mimetypes.add_type("image/vnd.microsoft.icon", ".ico")
    mimetypes.add_type("image/gif", ".gif")
    mimetypes.add_type("font/woff", ".woff")
    mimetypes.add_type("application/manifest+json", ".webmanifest")


def start_swingmusic(host: str, port: int, debug: bool, base_path:pathlib.Path):
    """
    Creates and starts the Flask application server for Swing Music.

    This function sets up the Flask application with all necessary
    configurations, including static file handling, authentication middleware, and
    server setup, then runs it. It also sets up background tasks and cron jobs.

    Args:
        host (str): The host address to bind the server to (e.g., 'localhost' or '0.0.0.0')
        port (int): The port number to run the server on
        debug (bool): If swingmusic should start in debug mode
        base_path (Path): On which pathe to store config

    Note:
        The application uses either bjoern or waitress as the WSGI server,
        depending on availability. It also includes JWT authentication,
        static file serving with gzip compression support, and automatic
        token refresh functionality.
    """

    # Example: Setting up dirs, database, and loading stuff into memory.
    # TIP: Be careful with the order of the setup functions.
    settings.Paths(base_path)
    setup_logger(debug=debug)

    config_mimetypes()
    run_setup()

    @background
    def run_swingmusic():
        register_plugins()

        setproctitle.setproctitle(f"swingmusic {host}:{port}")
        start_cron_jobs()


    app = app_builder()

    log_startup_info(host, port)
    load_into_mem()
    run_swingmusic()
    # TrackStore.export()
    # ArtistStore.export()

    try:
        import bjoern

        bjoern.run(app, host, port)
    except ImportError:
        import waitress

        waitress.serve(
            app,
            host=host,
            port=port,
            threads=100,
            ipv6=True,
            ipv4=True,
        )