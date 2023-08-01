from typing import Any
from django.core.management.base import BaseCommand
from digisac.api import request_utils
from protocols.update_database import update

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        print('OK')
        # api = request_utils.DigisacConfigRequest()
        # json = api.get_historic(start_period='01/01/2023', end_period='31/01/2023')
        # update.update(json)