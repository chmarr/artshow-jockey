from .models import Announcement

def get_announcement_counts(user, announcements=None):
    if announcements is None:
        announcements = Announcement.objects.active()
    total = new = new_and_important = 0
    if user and user.is_authenticated():
        for a in announcements:
            total += 1
            if not a.is_seen_by(user):
                new += 1
                if a.important:
                    new_and_important += 1
    return total, new, new_and_important
