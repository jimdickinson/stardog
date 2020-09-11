import logging
import cherrypy

logger = logging.getLogger('execute_query')

@cherrypy.expose
@cherrypy.tools.json_out()
@cherrypy.tools.json_in()
class ExecuteQueryEndpoint:
    def POST(self):
        return '{"lets": "go"}'
