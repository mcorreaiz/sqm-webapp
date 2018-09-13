import sys

APP_URL = 'notas-sqm.azurewebsites.net'
PREFERRED_URL_SCHEME = 'https'
MONGODB_HOST = 'mongodb://127.0.0.1:27017'
ALLOWED_EXTENSIONS = set(['doc', 'docx'])
DEBUG_TB_PANELS = ['flask_debugtoolbar.panels.versions.VersionDebugPanel',
                    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
                    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                    'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
                    'flask_debugtoolbar.panels.template.TemplateDebugPanel',
                    'flask_debugtoolbar.panels.logger.LoggingPanel',
                    'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
                    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
                    'flask_mongoengine.panels.MongoDebugPanel']
MAIL_SERVER ='smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
