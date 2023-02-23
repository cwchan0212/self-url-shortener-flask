import urllib.parse as up
import os
from flask import Flask


def fullpath_database_uri(db_uri):
    basedir = str(os.getcwd()).replace("\\", "/")
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_name = db_uri.replace("sqlite:///", "")
    db_filepath = f"sqlite:///{basedir}/instance/{db_name}"
    return db_filepath


app = Flask(__name__ )
app.config.from_prefixed_env()
from url_shortener import views

app.config["PERMANENT_SESSION_LIFETIME"] = app.config["PERMANENT_SESSION_LIFETIME"] * 60
app.config["MAX_CONTENT_LENGTH"] = app.config['MAX_CONTENT_LENGTH'] * 1024 * 1024

# ---------------------------------------------------------------------------------------------------------------------
# Connect to ElephantSQL
# 
remote = 0
if remote:
    db_host = app.config["DB_HOST"]
    db_user = app.config["DB_USERNAME"]
    db_pass = app.config["DB_PASSWORD"]
    db_name = app.config["DB_USERNAME"]

    database_uri = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}/{db_name}"
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
# ---------------------------------------------------------------------------------------------------------------------
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = fullpath_database_uri(app.config['SQLALCHEMY_DATABASE_URI'])

print(f" # It is a {app.config['ENV']} mode.")
# print(f" # {app.config['SQLALCHEMY_DATABASE_URI']} ")
# print(f" # {app.config['DB_URL']} ")

# =====================================================================================================================
# Note
# ---------------------------------------------------------------------------------------------------------------------
# Generate requirements.txt
# pip freeze > requirements.txt

# Install requirements.txt
# pip install -r requirements.txt --use-pep517

# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['SQLALCHEMY_RECORD_QUERIES'] = True

# app.config['DEBUG_TB_PANELS'] = [    'flask_debugtoolbar.panels.versions.VersionDebugPanel',    'flask_debugtoolbar.panels.timer.TimerDebugPanel',    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',    'flask_debugtoolbar.panels.template.TemplateDebugPanel',    'flask_debugtoolbar.panels.logger.LoggingPanel',    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',    'flask_sqlalchemy.panels.SQLAlchemyDebugPanel',]


# toolbar = DebugToolbarExtension(app)

