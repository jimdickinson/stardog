import os
import cherrypy
from cherrypy.lib.static import serve_file
from stardog.endpoints.execute_query import ExecuteQueryEndpoint
from stardog.endpoints.new_document import NewDocumentEndpoint
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('stardog.endpoints', 'resources'),
    autoescape=select_autoescape(['html', 'xml'])
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
class StardogServer:
    @cherrypy.expose
    def static(self, name):
        if name.endswith('css'):
            return serve_file(os.path.join(CURRENT_DIR, 'stardog', 'endpoints', 'resources', 'static', name), content_type='text/css')
        if name.endswith('svg'):
            return serve_file(os.path.join(CURRENT_DIR, 'stardog', 'endpoints', 'resources', 'static', name), content_type='image/svg+xml')

    @cherrypy.expose
    def query(self, name):
        if name == 'index.html':
            template = env.get_template(name)
            return template.render({'pods': [{'name': 'Pod1'}, {'name': 'Pod2'}, {'name': 'Pod3'}]})

        raise cherrypy.HTTPError(404, message="Resource Not Found")

    @cherrypy.expose
    def item(self, name):
        if name.endswith('js'):
            return serve_file(os.path.join(CURRENT_DIR, 'stardog', 'endpoints', 'resources', name), content_type='text/javascript')
        template = env.get_template('item_explorer.html')
        return template.render({'name': name})

class Api:
    pass

CHERRY_TREE_CONFIG = {
    '/api/executeQuery': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json')],
    },
    '/api/newDocument': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'application/json')],
    }
}

def setup_cherry_tree(port=8080):
    # Don't show traceback as HTML to the client on error
    # Run as if we're in production (so no 'debug' mode)
    cherrypy.config.update({
        'server.socket_port': port,
        'environment': 'production',
        'log.screen': True,
        'show_tracebacks': True,
    })
    service = StardogServer()
    service.api = Api()
    service.api.executeQuery = ExecuteQueryEndpoint()
    service.api.newDocument = NewDocumentEndpoint()
    return service

def startup_server():
    # Three endpoints, defined here:
    # /query (returns HTML)
    # /api/executeQuery
    # /api/newDocument
    service = setup_cherry_tree()
    print('Stardog server running on port 8080')
    cherrypy.quickstart(service, '/', CHERRY_TREE_CONFIG)

if __name__ == '__main__':
    startup_server()