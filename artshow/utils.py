from django.conf import settings
import re, csv, codecs, cStringIO


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


artshow_settings = AttributeFilter ( settings, r"ARTSHOW_|SITE_NAME$|SITE_ROOT_URL$" )


class UnicodeCSVWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([unicode(s).encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)