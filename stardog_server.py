import cherrypy
from stardog.endpoints.query_frontend import QueryEndpoint
from stardog.endpoints.execute_query import ExecuteQueryEndpoint
from stardog.endpoints.new_document import NewDocumentEndpoint

class StardogServer:
    pass

class Api:
    pass

CHERRY_TREE_CONFIG = {
    '/query': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'text/html')],
    },
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
        'log.screen': False,
        'show_tracebacks': False,
    })
    service = StardogServer()
    service.query = QueryEndpoint()
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