import os
import cherrypy
import requests
import uuid
import json
from urllib.parse import urlparse
from cherrypy.lib.static import serve_file
from jinja2 import Environment, PackageLoader, select_autoescape

# Environment variables to connect to Astra
ASTRA_BASE_URL_ENV = "BASE_URL" # e.g. https://asdfasdfadsf-us-east1.apps.astra.datastax.com/
ASTRA_USERNAME = "ASTRA_USERNAME"
ASTRA_PASSWORD = "ASTRA_PASSWORD"

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

def api_url(path):
    baseurl = os.getenv(ASTRA_BASE_URL_ENV)
    o = urlparse(baseurl)
    o = o._replace(path=path)
    return o.geturl()

def authenticate():
    username = os.getenv(ASTRA_USERNAME)
    password = os.getenv(ASTRA_PASSWORD)
    url = api_url('/api/rest/v1/auth')
    payload = {"username": username, "password": password}
    headers = {'accept': '*/*',
               'content-type': 'application/json'}

    # make auth request to Astra
    r = requests.post(url, 
                      data=json.dumps(payload), 
                      headers=headers)

    # extract and return the auth token 
    data = json.loads(r.text)
    return data["authToken"]

class Proxy:
    def __init__(self):
        self.token = None

    @cherrypy.expose
    def default(self, *args, **kwargs):
        # get the correct request uri for astra
        request_uri = cherrypy.request.request_line.split()[1]
        request_uri_parsed = urlparse(request_uri)
        api_base_parsed = urlparse(os.getenv(ASTRA_BASE_URL_ENV))

        # The path of the request should be the same as the one we proxy to,
        # but we need to fix the scheme and hostname/port.
        apiuri_parsed = request_uri_parsed._replace(
            scheme=api_base_parsed.scheme, netloc=api_base_parsed.netloc
        )
        apiuri = apiuri_parsed.geturl()

        content = cherrypy.request.body.read()

        api_request_headers = {}
        for (header, header_value) in cherrypy.request.header_list:
            if not ( header.lower() in ('remote-addr', 'host', 'user-agent', 'content-length') ):
                api_request_headers[header] = header_value

        # Get the appropriate requests function for this http method
        req_func = getattr(requests, cherrypy.request.method.lower())

        def do_api_request():
            # if we have a token, use it
            if self.token:
                api_request_headers['x-cassandra-token'] = self.token

            return req_func(apiuri, data=content, headers=api_request_headers, verify=False)
        
        api_resp = do_api_request()

        if api_resp.status_code in (401, 403, 500):
            # hmmm.... didn't work... maybe we have no token or an expired one?
            self.token = authenticate()
            api_resp = do_api_request()
        
        cherrypy.response.status = api_resp.status_code
        
        for (header, header_value) in api_resp.headers.items():
            if not ( header.lower() in ('content-length', 'server') ):
                cherrypy.response.headers[header] = header_value

        return api_resp.content


CHERRY_TREE_CONFIG = {
}

def setup_cherry_tree(port=8080):
    # Don't show traceback as HTML to the client on error
    # Run as if we're in production (so no 'debug' mode)
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': port,
        'environment': 'production',
        'log.screen': True,
        'show_tracebacks': True,
    })
    service = StardogServer()
    service.api = Proxy()
    return service

def startup_server():
    # Three endpoints, defined here:
    # /query (returns HTML)
    # /api/executeQuery
    # /api/newDocument
    service = setup_cherry_tree()
    print('Stardog server running on port 8080')
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(service, '/', CHERRY_TREE_CONFIG)

if __name__ == '__main__':
    startup_server()