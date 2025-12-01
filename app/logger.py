import logging
import configparser

from logging.handlers import RotatingFileHandler

def init(app):
    config = configparser.ConfigParser()

    try:
        config_location = "etc/logging.cfg"
        config.read(config_location)

        app.config['DEBUG'] = config.get("config", "debug")
        app.config['ip-address'] = config.get("config", "ip_address")
        app.config['port'] = config.get("config", "port")
        app.config['url'] = config.get("config", "url")

        app.config['log_file'] = config.get("logging", "name")
        app.config['log_location'] = config.get("logging", "location")
        app.config['log_level'] = config.get("logging", "level")
        
        app.config['thesportsdb_apikey'] = config.get("apiKeys", "thesportsdb")
        app.config['secretkey'] = config.get("apiKeys", "secretkey")

    except:
        print("Could not read config file from: " + config_location)

def logs(app):
    log_pathname = app.config['log_location'] + app.config['log_file']
    open(log_pathname, 'w').close()
    
    file_handler = RotatingFileHandler(log_pathname, maxBytes=1024*1024*10, backupCount =1024)
    file_handler.setLevel(app.config['log_level'])
    
    formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s")
    file_handler.setFormatter(formatter)
    
    app.logger.setLevel(app.config['log_level'])
    app.logger.addHandler(file_handler)