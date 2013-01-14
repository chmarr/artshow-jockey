from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings

class Person ( models.Model ):
	name = models.CharField ( max_length = 100 )
	address1 = models.CharField ( max_length = 100, blank=True )
	address2 = models.CharField ( max_length = 100, blank=True )
	city = models.CharField ( max_length = 100, blank=True )
	state = models.CharField ( max_length = 40, blank=True )
	postcode = models.CharField ( max_length = 20, blank=True )
	country = models.CharField ( max_length = 40, blank=True )
	phone = models.CharField ( max_length = 40, blank=True )
	email = models.CharField ( max_length = 100, blank=True )
	reg_id = models.CharField ( max_length = 40, blank=True )
	comment = models.CharField ( max_length = 100, blank=True )
	def __unicode__ ( self ):
		if self.reg_id or self.comment:
			return "%s (%s)" % ( self.name, ",".join([x for x in (self.reg_id,self.comment) if x ]) )
		else:
			return self.name
	def clickable_email ( self ):
		return '<a href="mailto:%s">%s</a>' % ( self.email, self.email )
	clickable_email.allow_tags = True
	def mailing_label ( self ):
		return u'<a href="javascript:w=window.open(\'%s\',\'blank\',\'toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=300,height=100\');">ML&rarr;</a>' % ( reverse('person-mailing-label',args=(self.pk,)), )
		# return '<a href="%s">ML</a>' % urlresolvers.reverse('artshow.views.artist_mailing_label',args=(self.pk,))
		return "Hello"
	mailing_label.allow_tags = True
	def get_mailing_label ( self ):
			lines = [ self.name ]
			if self.address1: lines.append ( self.address1 )
			if self.address2: lines.append ( self.address2 )
			lines.append ( " ".join ( [ x for x in ( self.city, self.state, self.postcode ) if x ] ) )
			if self.country and self.country != settings.PEEPS_DEFAULT_COUNTRY:
					lines.append ( self.country )
			return "\n".join ( lines )
	class Meta:
		verbose_name_plural = "People"
