from django.core.management.base import BaseCommand, CommandError
from robot.algorithm import get_all_clients

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'

#    def add_arguments(self, parser):
#        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
#            try:
#                poll = Poll.objects.get(pk=poll_id)
#            except Poll.DoesNotExist:
#                raise CommandError('Poll "%s" does not exist' % poll_id)

#            poll.opened = False
#            poll.save()
            for client in get_all_clients():
                self.stdout.write(client.lfm)

            self.stdout.write('Successfully ran evaluations')
