from flask import Flask
# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__ )
# app = application
app.config.from_prefixed_env()
from url_shortener import views
app.config["PERMANENT_SESSION_LIFETIME"] = app.config["PERMANENT_SESSION_LIFETIME"] * 60
app.config["MAX_CONTENT_LENGTH"] = app.config['MAX_CONTENT_LENGTH'] * 1024 * 1024
print(f" # It is a {app.config['ENV']} mode.")
print(f" # {app.config['SQLALCHEMY_DATABASE_URI']} ")
# Generate requirements.txt
# pip freeze > requirements.txt

# Install requirements.txt
# pip install -r requirements.txt --use-pep517

# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['SQLALCHEMY_RECORD_QUERIES'] = True

# app.config['DEBUG_TB_PANELS'] = [    'flask_debugtoolbar.panels.versions.VersionDebugPanel',    'flask_debugtoolbar.panels.timer.TimerDebugPanel',    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',    'flask_debugtoolbar.panels.template.TemplateDebugPanel',    'flask_debugtoolbar.panels.logger.LoggingPanel',    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',    'flask_sqlalchemy.panels.SQLAlchemyDebugPanel',]


# toolbar = DebugToolbarExtension(app)

