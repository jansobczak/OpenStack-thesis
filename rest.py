import random
import string
import cherrypy


class ReservationWebService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        return cherrypy.session['mystring']

    def POST(self, length=8):
        some_string = ''.join(random.sample(string.hexdigits, int(length)))
        cherrypy.session['mystring'] = some_string
        return some_string

    def PUT(self, another_string):
        cherrypy.session['mystring'] = another_string

    def DELETE(self):
        cherrypy.session.pop('mystring', None)

#Start the REST service
if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch':
            cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers':
            [('Content-Type', 'text/plain')],
        }
    }

cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 8080
cherrypy.quickstart(ReservationWebService(), '/', conf)
