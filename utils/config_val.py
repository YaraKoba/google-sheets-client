import configparser


def load_config():
    conf = configparser.ConfigParser()
    conf.read('./config.ini')
    return conf

