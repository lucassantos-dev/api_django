from typing import Any
from django.core.management.base import BaseCommand
from digisac.api_digisac import request_utils
from protocols.update_database import update
from protocols.models import Protocol

def get_protocol_times(protocol_number):
    try:
        # Pesquisar o protocolo com base no número fornecido
        protocol = Protocol.objects.get(protocol_number=protocol_number)
        return f'primeiro tempo de espera : {protocol.first_waiting_time}\n', f'tempo total :{protocol.total_attendance_time}\n', f'média: {protocol.average_waiting_time}\n'

    except Protocol.DoesNotExist:
        return None, None, None

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        api = request_utils.DigisacConfigRequest()
        json = api.get_historic(start_period='03/01/2023', end_period='04/01/2023')
        # json = api.get_historic()
        update.update(json)
        # print(get_protocol_times('2023080335351'))