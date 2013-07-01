from django.db import models
from django.db.models import Q, Count
from django.contrib.auth.models import User
import datetime
from django.utils import timezone


class AnnouncementManager(models.Manager):

    def active(self):
        now = timezone.now()
        query = self.get_query_set().filter(Q(created__lt=now), (Q(expires__isnull=True) | Q(expires__gt=now)))
        return query


class Announcement(models.Model):

    objects = AnnouncementManager()

    subject = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    author = models.ForeignKey(User)
    important = models.BooleanField(default=False)
    created = models.DateTimeField()
    expires = models.DateTimeField(null=True, blank=True)

    def is_seen_by(self, user):
        return self.announcementseen_set.filter(user=user).exists()

    def mark_seen(self, user):
        try:
            self.announcementseen_set.get(user=user)
        except AnnouncementSeen.DoesNotExist:
            ann_seen = AnnouncementSeen(announcement=self, user=user)
            ann_seen.save()

    def __unicode__(self):
        return "%s by %s" % (self.subject, self.author)


class AnnouncementSeen(models.Model):

    announcement = models.ForeignKey(Announcement)
    user = models.ForeignKey(User)
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('announcement', 'user'))

    def __unicode__(self):
        return "%s seen by %s" % (self.announcement.subject, self.user)
