import sys

class Config():
    DEBUG = False
    MONGODB_HOST = 'mongodb://mcorreaiz:zbcI6fmYSvC1pOIufP2gYzo9Gk2O5UCDVH87T8zTrocEj8NpvWeQgeXS3aDIZLRzGx9Oa2zBsVOjWPk8fO5nfA==@mcorreaiz.documents.azure.com:10255/dev?ssl=true&replicaSet=globaldb'
    SECRET_KEY = 'password'
    ALLOWED_EXTENSIONS = set(['docx'])


class ProductionConfig(Config):
    MONGODB_HOST = 'mongodb://mcorreaiz:zbcI6fmYSvC1pOIufP2gYzo9Gk2O5UCDVH87T8zTrocEj8NpvWeQgeXS3aDIZLRzGx9Oa2zBsVOjWPk8fO5nfA==@mcorreaiz.documents.azure.com:10255/prod?ssl=true&replicaSet=globaldb'

class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    DEBUG_TB_PANELS = ['flask_debugtoolbar.panels.versions.VersionDebugPanel',
                        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
                        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
                        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
                        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
                        'flask_debugtoolbar.panels.logger.LoggingPanel',
                        'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
                        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
                        'flask_mongoengine.panels.MongoDebugPanel']

def get_config(mode):
    deploy_mode = {'PROD': ProductionConfig,
                'DEV': DevelopmentConfig}
    try:
        config = deploy_mode[mode]
        print('{} Environment'.format(mode), file=sys.stderr)
    except KeyError:
        config = deploy_mode['DEV']
        print("Incorrect or missing deploy mode, defaulting to DEV", file=sys.stderr)
    return config
