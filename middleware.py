class SimpleMiddleWare(object):
	def __init__(self, app):
		self.app = app
	def __call__(self, environ, start_response):
		print('oh hey')
		return self.app(environ, start_response)
