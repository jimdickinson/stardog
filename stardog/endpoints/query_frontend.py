
import logging
import cherrypy

logger = logging.getLogger('query_frontend')

@cherrypy.expose
class QueryEndpoint:
    def GET(self):
        return "<html>it is go time</html>"