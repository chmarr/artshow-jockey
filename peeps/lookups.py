from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from django.db.models.loading import get_model
from django.conf import settings
from django.core.urlresolvers import reverse

class PersonLookup(LookupChannel):

	model = get_model ( *settings.ARTSHOW_PERSON_CLASS.split('.',1) )

	def get_query(self,q,request):
		return self.model.objects.filter(Q(name__icontains=q) | Q(email__istartswith=q) | Q(reg_id__istartswith=q)).order_by('name')

	def get_result(self,obj):
		u""" result is the simple text that is the completion of what the person typed """
		return obj.name
		
	def add_common_bits ( self, obj, parts ):
		if obj.reg_id:
			parts.append ( "<div><i>Reg ID: %s</i></div>" % escape(obj.reg_id) )
		if obj.city or obj.state or obj.country:
			parts.append ( "<div><i>%s</i></div>" % escape( " ".join ( [ x for x in [ obj.city, obj.state, obj.country ] if x ] ) ) )
		if obj.comment:
			parts.append ( "<div><i>%s</i></div>" % escape(obj.comment) )

	def format_match(self,obj):
		""" (HTML) formatted item for display in the dropdown """
		parts = [ "<div>%s</div>" % escape(obj.name) ]
		if obj.email:
			parts.append ( "<div><i>%s</i></div>" % escape(obj.email) )
		self.add_common_bits ( obj, parts )
		return "".join ( parts )

	def format_item_display(self,obj):
		""" (HTML) formatted item for displaying item in the selected deck area """
		## TODO - misusing the showAddAnotherPopup function only kinda works.
		parts = [ "<div><a href=\"%s\" class=\"ui-icon ui-icon-pencil\" onclick=\"return showAddAnotherPopup(this);\">E</a></div><div>%s</div>" % 
				( reverse("admin:peeps_person_change", args=(obj.id,) ), escape(obj.name) ) ]
		if obj.email:
			parts.append ( "<div><a href=\"mailto:%s\"><i>%s</i></a></div>" % ( escape(obj.email), escape(obj.email) ) )
		self.add_common_bits ( obj, parts )
		return "".join ( parts )
