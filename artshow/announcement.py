# TODO Make the announcement package configurable
from django.contrib.auth.decorators import login_required
from artshow.utils import artshow_settings
from tinyannounce.models import Announcement
from django.shortcuts import render, redirect, get_object_or_404


@login_required
def index(request):
    announcements = Announcement.objects.active().order_by('-created')

    for a in announcements:
        a.is_seen = a.is_seen_by(request.user)

    return render(request, "artshow/announcement_index.html",
           {'artshow_settings': artshow_settings, 'announcements': announcements})


@login_required
def show(request, announcement_id):

    announcement = get_object_or_404(Announcement, pk=announcement_id)
    is_seen = announcement.is_seen_by(request.user)

    if request.method == "POST":
        announcement.mark_seen(request.user)
        return redirect(index)

    return render(request, "artshow/announcement_show.html",
        {'artshow_settings':artshow_settings, 'announcement': announcement,
         'is_seen':is_seen})
