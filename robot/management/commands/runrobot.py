from django.core.management.base import BaseCommand
from robot.algorithm import write_off

class Command(BaseCommand):
    help = 'Runs the evaluation values and prices'
    def handle(self, *args, **options):
            write_off()
            self.stdout.write('Successfully ran evaluations')
