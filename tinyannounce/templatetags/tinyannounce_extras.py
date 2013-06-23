from django import template
from tinyannounce.models import Announcement

register = template.Library()


@register.inclusion_tag("tinyannounce/announcements_available.html", takes_context=True)
def announcements_available(context):
    user = context['request'].user
    announcements = Announcement.objects.active()
    total = new = new_and_important = 0
    for a in announcements:
        total += 1
        if not a.is_seen_by(user):
            new += 1
            if a.important:
                new_and_important += 1
    return {'announcements': announcements, 'total': total, 'new': new, 'new_and_important': new_and_important}

