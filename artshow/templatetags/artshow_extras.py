from django import template

try:
    from tinyannounce import get_announcement_counts
except ImportError:
    get_announcement_counts = None

register = template.Library()

@register.inclusion_tag("artshow/navigation_bar.html", takes_context=True)
def nagivation_bar(context):
    user = context['request'].user
    if user and not user.is_authenticated():
        user = None
    announcement_counts = {}
    if get_announcement_counts is not None:
        announcement_counts['total'], announcement_counts['new'], announcement_counts['new_and_important'] = \
                get_announcement_counts(user)
    return {'user': user, 'has_add_invoice': user and user.has_perm('artshow.add_invoice'),
            'is_artshow_staff': user and user.has_perm('artshow.is_artshow_staff'),
            'announcement_counts': announcement_counts}
