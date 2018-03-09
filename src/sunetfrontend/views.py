# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import re

from flask import Blueprint, current_app, request, abort, jsonify


__author__ = 'ft'

sunetfrontend_views = Blueprint('sunetfrontend', __name__, url_prefix='')


@sunetfrontend_views.route('/register/<backend>', methods=['POST'])
def register(backend):
    """
    Register a backend server.

    Example:

      POST to /register/www.dev.eduid.se with the following form variables:

        server=www-fre-1
        port=2443

      results in a file containing

        ACTION=register
        BACKEND=www.dev.eduid.se
        SERVER=www-fre-1
        REMOTE_IP=<remote IP address>
        PORT=2443

    This file is then found and processed by something else that generates
    actual load balancer config.
    """
    remote_ip = _get_remote_ip()
    server = ''
    port = 0
    try:
        server = request.form['server']
        port = int(request.form.get('port', 443))
    except:
        current_app.logger.info('Bad server and/or port POST parameter')
        abort(400)

    if not is_allowed_register(backend, server, remote_ip):
        current_app.logger.info('Register for backend {} by server {} NOT ALLOWED'.format(
            backend, server))
        abort(403)

    current_app.logger.info('Register backend {}, server {}, port {}'.format(backend, server, port))

    write_file('register', backend, server, remote_ip, port)

    current_app.logger.debug('Returning success')
    return jsonify({'success': True})


@sunetfrontend_views.route('/unregister/<backend>', methods=['POST'])
def unregister(backend):
    """
    Unregister a backend server.

    Example:

      POST to /unregister/www.dev.eduid.se with the following form variables:

        server=www-fre-1

      will remove the haproxy snippet file for that server.
    """
    remote_ip = _get_remote_ip()
    server = ''
    port = 0
    try:
        server = request.form['server']
        port = int(request.form.get('port', 443))
    except:
        current_app.logger.info('Bad server POST parameter')
        abort(400)

    if not is_allowed_register(backend, server, remote_ip):
        current_app.logger.info('Unregister for backend {} by server {} NOT ALLOWED'.format(
            backend, server))
        abort(403)

    current_app.logger.info('Unregister backend {}, server {}'.format(backend, server))

    # Signal explicit un-registration so that route can be withdrawn
    write_file('unregister', backend, server, remote_ip, port)


@sunetfrontend_views.route('/ping', methods=['GET', 'POST'])
def ping():
    return 'pong\n'


def is_allowed_register(backend, server, remote_ip):
    # TODO: implement this
    return True


def write_file(action, backend, server, remote_ip, port):
    server_fn = _get_server_filename(backend, server, remote_ip)
    current_app.logger.debug('Writing file {}'.format(server_fn))
    with open(server_fn, 'w') as fd:
        fd.write('ACTION={}\nBACKEND={}\nSERVER={}\nREMOTE_IP={}\nPORT={}\n'.format(
            action, backend, server, remote_ip, port))

    current_app.logger.debug('Returning success')
    return jsonify({'success': True})


def _get_remote_ip():
    if request.headers.getlist('X-Forwarded-For'):
        return request.headers.getlist('X-Forwarded-For')[0]
    return request.remote_addr


def _get_server_filename(backend, server, remote_ip):
    if not re.match('[a-zA-Z0-9_.-]+', backend):
        current_app.logger.info('Illegal characters in backend {}'.format(backend))
        abort(400)

    if not re.match('[a-zA-Z0-9_.-]+', server):
        current_app.logger.info('Illegal characters in server {}'.format(server))
        abort(400)

    if not re.match('[a-fA-F0-9:.]+', remote_ip):
        current_app.logger.info('Illegal characters in remote_ip {}'.format(server))
        abort(400)

    be_dir = os.path.join(current_app.config.get('BACKEND_DIR'), backend)
    if not os.path.isdir(be_dir):
        current_app.logger.info('Register of unknown backend {}'.format(backend))
        abort(403)

    return os.path.join(be_dir, server + '_' + remote_ip + '.conf')
