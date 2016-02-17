import ConfigParser

config_file_path = '/home/ec2-user/bblio/bblio.cfg'

def get_config():
    config = ConfigParser.ConfigParser()
    config.read(config_file_path)
    return config

def set_config(config):
    with open(config_file_path, 'wb') as configfile:
        config.write(configfile)

