#!/usr/bin/python

# Enter the virtualenv
import os.path
_activate = os.path.join(os.path.dirname(__file__),
                         'env/bin/activate_this.py')
execfile(_activate, dict(__file__=_activate))

# Add our code to path.
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),
                             'web_scripts/kdc'))

from werkzeug.exceptions import NotFound
from werkzeug.wsgi import SharedDataMiddleware, DispatcherMiddleware

import kdc

def create_app():
    """
    Serves the entire mess, including hack to make index.html work.
    """
    kdc_app = kdc.create_app()

    def _throw_not_found(e, s): raise NotFound()

    web_scripts = os.path.join(os.path.dirname(__file__), 'web_scripts')
    app = DispatcherMiddleware(
        SharedDataMiddleware(_throw_not_found, { '/': web_scripts, }),
        { '/kdc': kdc_app, })

    def _index_html_hack(environ, start_response):
        try:
            return app(environ, start_response)
        except NotFound, e:
            environ['PATH_INFO'] = environ.get('PATH_INFO', '') + '/index.html'
            try:
                return app(environ, start_response)
            except NotFound, e:
                return e(environ, start_response)
    return _index_html_hack

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
