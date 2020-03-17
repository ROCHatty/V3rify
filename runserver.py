"""
This script runs the V3rmillionDab application using a development server.
"""

from os import environ
from V3rmillionDab import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    app.run(HOST, 8080)
