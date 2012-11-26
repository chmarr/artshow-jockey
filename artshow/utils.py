from django.conf import settings
import re


class AttributeFilter (object):

	"""This creates a proxy object that will only allow
	access to the proxy if the attribute matches the
	regular expression. Otherwise,
	an AttributeError is returned."""
	
	def __init__ ( self, target, expression ):
		"""'target' is the object to be proxied. 'expression' is a regular expression
		(compiled or not) that will be used as the filter."""
		self.__target = target
		self.__expression = expression
		if not hasattr ( self.__expression, 'match' ):
			self.__expression = re.compile ( self.__expression )
			
	def __getattr__ ( self, name ):
		if self.__expression.match ( name ):
			return self.__target.__getattr__ ( name )
		else:
			raise AttributeError ( "AttributeFilter blocked access to '%s' on object '%s'" % ( name, self.__target ) )


artshow_settings = AttributeFilter ( settings, r"ARTSHOW_" )