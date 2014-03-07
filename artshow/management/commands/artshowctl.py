from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    args = 'command [options ...]'
    help = "Apply a command (applywonstatus)"

    def handle(self, *args, **options):

        command = args[0]
        method = getattr(self, "command_" + command)
        return method(*args[1:], **options)

    # noinspection PyUnusedLocal
    def command_applywonstatus(self, *args, **options):

        for p in Piece.objects.filter(status=Piece.StatusInShow, voice_auction=False):
            try:
                top_bid = p.top_bid()
            except Bid.DoesNotExist:
                pass
            else:
                p.status = Piece.StatusWon
                p.save()
