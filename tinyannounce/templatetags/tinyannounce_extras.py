from django import template
from ..models import Announcement
from ..views import get_announcement_counts

register = template.Library()


@register.inclusion_tag("tinyannounce/announcements_available.html", takes_context=True)
def announcements_available(context):
    user = context['request'].user
    announcements = Announcement.objects.active()
    total, new, new_and_important = get_announcement_counts(user, announcements)
    return {'announcements': announcements, 'total': total, 'new': new, 'new_and_important': new_and_important}

