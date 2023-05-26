import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def getter_setting():
    secret_key = "g3oyjc*b03dz1%98f#*4a*6*!p%8@qr)uzw$x0te)bdfk(!l29"
    host = '127.0.0.1'
    db_name = 'fatedeck_db'
    user = 'root'
    password = 'iwdtfw_404'
    port = 3306
    # utf8mb4 used to allow 4byte characters.
    charset = 'utf8mb4'
    db_engine = 'django.db.backends.mysql',
    email = 't.barbato78@gmail.com',
    debug_value = True
    return debug_value, secret_key, host, db_name, user, password, port, \
        charset, db_engine, email

"""def getter_setting():
    secret_key = "g3oyjc*b03dz1%98f#*4a*6*!p%8@qr)uzw$x0te)bdfk(!l29"
    host = 'fatedeck.mysql.pythonanywhere-services.com'
    db_name = 'fatedeck$fatedeck_db'
    user = 'fatedeck'
    password = 'sohednebropwaifnist3'
    port = 3306
    charset = 'utf-8'
    db_engine = 'django.db.backends.mysql',
    email = 't.barbato78@gmail.com',
    debug_value = False
    return debug_value, secret_key, host, db_name, user, password, port, \
        charset, db_engine, email
"""


def getter_db_only():
    host = 'localhost'
    db_name = os.path.join(BASE_DIR, 'fatedeck_db')
    user = 'root'
    password = 'iwdtfw_404'
    return host, db_name, user, password
