from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'My Appointments'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = 'd7c965e8-0685-477a-baae-087e7372943f'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''