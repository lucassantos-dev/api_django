from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta, date
from ...models import Protocol
from django.utils.translation import gettext as _
from django.utils import timezone
from attendants.models import Attendant


class ProtocolStatisticsView(APIView):
    """
    API View para obter estatísticas de protocolos.
    Endpoint: /api/protocol-statistics/
    Resposta JSON:
    {
        "total_calls": 100,
        "average_waiting_time": "02:30:00",
        "average_daily_calls": 5
    }
    """

    def is_business_day(self, date_to_check):
        # Verificar se é um dia útil (segunda a sexta, onde 0 é segunda-feira e 4 é sexta-feira)
        return date_to_check.weekday() < 5 and date_to_check

    def count_business_days_until_today(self):
        today = date.today()
        start_date = date(today.year, 1, 1)
        business_days_count = 0
        current_date = start_date
        while current_date <= today:
            if self.is_business_day(current_date):
                business_days_count += 1
            current_date += timedelta(days=1)

        return business_days_count

    def formatar_duracao(self, duracao):
        total_segundos = duracao.total_seconds()

        horas = int(total_segundos // 3600)
        minutos = int((total_segundos % 3600) // 60)
        segundos = int(total_segundos % 60)

        if horas > 0:
            return f"{horas} horas e {minutos} minutos"
        elif minutos > 0:
            return f"{minutos} minutos"
        else:
            return f"{segundos} segundos"

    def post(self, request):
        today = timezone.now()
        data = request.data
        tax_protocolo_attendant = Attendant.objects.get(name="Tax Protocolo")
        programacao_attendant = Attendant.objects.get(name="Programação")
        # -
        year = data.get("years", [])
        #  Filtra os protocolos pelo ano, se o filtro for fornecido
        if year and isinstance(year, int):
            protocols_this_year = Protocol.objects.filter(start_date__year=year)
        else:
            protocols_this_year = Protocol.objects.filter(start_date__year=today.year)
        protocols_this_year = protocols_this_year.exclude(
            attendant=tax_protocolo_attendant
        )
        protocols_this_year = protocols_this_year.exclude(
            attendant=programacao_attendant
        )
        total_calls = protocols_this_year.count()
        filtered_protocols = protocols_this_year.filter(
            first_waiting_time__isnull=False,
            is_business_hours=True,
            is_from_me=False,
            first_waiting_time__lt=timedelta(hours=8),
        )
        total_waiting_time_seconds = sum(
            protocol.first_waiting_time.total_seconds()
            for protocol in filtered_protocols
        )
        average_waiting_time_seconds = total_waiting_time_seconds / len(
            filtered_protocols
        )
        average_waiting_time = timedelta(seconds=average_waiting_time_seconds)

        total_days = self.count_business_days_until_today()
        average_daily_calls = total_calls / total_days if total_days > 0 else 0

        return Response(
            {
                "total_calls": total_calls,
                "average_waiting_time": self.formatar_duracao(average_waiting_time),
                "average_daily_calls": round(average_daily_calls),
            }
        )
