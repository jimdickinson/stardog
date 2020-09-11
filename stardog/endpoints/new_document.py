import logging
import cherrypy

logger = logging.getLogger('new_document')

@cherrypy.expose
@cherrypy.tools.json_out()
@cherrypy.tools.json_in()
class NewDocumentEndpoint:
    def POST(self):
        return '{"lets": "post"}'