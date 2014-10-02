#!/usr/bin/env python3
import argparse
import flask
from http import server
import sys

app = flask.Flask(__name__, static_url_path='')

@app.route('/')
def index():
  return flask.render_template('index.html')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Testing server launcher')
  parser.add_argument('--port', '-p', help='Port for the web server', nargs='?', type=int, default=8080)
  parser.add_argument('--bind-interface', '-b', help='IP address to bind to', nargs='?', type=str,
                      default='localhost')
  parser.add_argument('--debug', '-d', help='Debug mode uses unminified javascript and server debug mode',
                      action='store_true')

  args = parser.parse_args()
  app.config['DEBUG'] = args.debug
  app.run(host=args.bind_interface, port=args.port, debug=args.debug)
