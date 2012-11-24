from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from django.db.models.loading import get_model
from django.conf import settings

class PersonLookup(LookupChannel):

	model = get_model ( *settings.ARTSHOW_PERSON_CLASS.split('.',1) )

	def get_query(self,q,request):
		return self.model.objects.filter(Q(name__icontains=q) | Q(email__istartswith=q) | Q(reg_id__istartswith=q)).order_by('name')

	def get_result(self,obj):
		u""" result is the simple text that is the completion of what the person typed """
		return obj.name

	def format_match(self,obj):
		""" (HTML) formatted item for display in the dropdown """
		return self.format_item_display(obj)

	def format_item_display(self,obj):
		""" (HTML) formatted item for displaying item in the selected deck area """
		parts = [ escape(obj.name) ]
		if obj.email:
			parts.append ( "<div><i>%s</i></div>" % escape(obj.email) )
		if obj.reg_id:
			parts.append ( "<div><i>Reg ID: %s</i></div>" % escape(obj.reg_id) )
		if obj.city or obj.state or obj.country:
			parts.append ( "<div><i>%s</i></div>" % escape( " ".join ( [ x for x in [ obj.city, obj.state, obj.country ] if x ] ) ) )
		if obj.comment:
			parts.append ( "<div><i>%s</i></div>" % escape(obj.comment) )
		return "".join ( parts )
