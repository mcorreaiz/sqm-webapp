import sys

# class Config():
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


# class ProductionConfig(Config):

# class DevelopmentConfig(Config):
#     DEBUG = True
#     TEMPLATES_AUTO_RELOAD = True
#     DEBUG_TB_PANELS = ['flask_debugtoolbar.panels.versions.VersionDebugPanel',
#                         'flask_debugtoolbar.panels.timer.TimerDebugPanel',
#                         'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
#                         'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
#                         'flask_debugtoolbar.panels.template.TemplateDebugPanel',
#                         'flask_debugtoolbar.panels.logger.LoggingPanel',
#                         'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
#                         'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
#                         'flask_mongoengine.panels.MongoDebugPanel']

# def get_config(mode):
#     deploy_mode = {'production': ProductionConfig,
#                 'development': DevelopmentConfig}
#     try:
#         config = deploy_mode[mode]
#         print('{} Environment'.format(mode), file=sys.stderr)
#     except KeyError:
#         config = deploy_mode['development']
#         print("Incorrect or missing deploy mode, defaulting to development", file=sys.stderr)
#     return config
