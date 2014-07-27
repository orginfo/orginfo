from accounting.models import Client

def get_all_clients():
    return Client.objects.all()

def write_of_cold_water_service(client):
    client.

def write_off():
    """Списание средств с клиентских счетов.

    Списание произодится раз в месяц 25 числа.
    """
    for client in Client.objects.all():
        is_cold_water_service = client.serviceclient_set.filter(
            service_name="Холодное водоснабжение").last()
        if is_cold_water_service:
            

