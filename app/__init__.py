import argparse
from app.models import Base
from sqlalchemy import create_engine
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

# Defining arguments and creating the args object
parser = argparse.ArgumentParser(allow_abbrev=False, description='A tool for passive threat intel based on DNS and SSL')
parser.add_argument('-f', '--file', dest='file', type=str, help='Give input filename', required=False)
parser.add_argument('-d', '--domain', dest='domain', type=str, help='Give input domain name', required=False)
parser.add_argument('-eA', '--export_all', dest='export_all_outfile', type=str, help='Export entire database to Excel with given filename', required=False)
parser.add_argument('-e', '--export', dest='export_outfile', type=str, help='Export current query response to Excel with given filename', required=False)
args = parser.parse_args()

# Define SQL database

# create engine
dbi_uri = Config.SQLALCHEMY_DATABASE_URI
engine = create_engine(dbi_uri, echo=False)

# create all tables
Base.metadata.create_all(engine)


# Define logging : file and console

if not os.path.exists('logs'):
    os.mkdir('logs')

# create logger with 'spam_application'
logger = logging.getLogger('collision')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
file_handler = logging.FileHandler('logs/collision.log')
file_handler.setLevel(Config.FILE_LOGGING_LEVEL)
# create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(Config.CONSOLE_LOGGING_LEVEL)
# create formatter and add it to the handlers
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
console_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)
# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.debug('Collision app has started')


from app import app, models
