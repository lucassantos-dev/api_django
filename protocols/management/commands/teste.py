from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        print('OK')