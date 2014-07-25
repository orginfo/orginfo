from accounting.models import Client

def get_all_clients():
    return Client.objects.all()
