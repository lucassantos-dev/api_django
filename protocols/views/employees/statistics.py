from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
from django.utils import timezone
from attendants.models import Attendant
from datetime import timedelta


class AttendantStatisticsView(APIView):
    """
    API View para obter estatísticas gerais dos atendentes.
    Endpoint: /api/attendant-statistics/
    Requisição JSON (opcional):
    {
        "year": 2023
    }
    Resposta JSON:
    {
        "average_handling_time": "00:05:00",
        "attendant_with_most_calls": "Attendant X",
        "attendant_with_least_calls": "Attendant Y"
    }
    """

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
        data = request.data
        year = data.get("year", None)

        today = timezone.now()

        # Filtra os protocolos pelo ano, se o filtro for fornecido
        if year and isinstance(year, int):
            protocols_this_year = Protocol.objects.filter(start_date__year=year)
        else:
            protocols_this_year = Protocol.objects.filter(start_date__year=today.year)

        # Exclui os atendentes "Tax Protocolo", "Programação" e "S/A"
        excluded_attendants = ["Tax Protocolo", "Programação", "S/A"]
        protocols_this_year = protocols_this_year.exclude(
            attendant__name__in=excluded_attendants
        )

        filtered_protocols = protocols_this_year.filter(
            first_waiting_time__isnull=False,
            is_business_hours=True,
            is_from_me=False,
            first_waiting_time__lt=timedelta(hours=8),
        )

        # Tempo médio de atendimento
        total_handling_time_seconds = sum(
            protocol.total_attendance_time.total_seconds()
            for protocol in filtered_protocols
            if protocol.total_attendance_time
        )

        average_handling_time_seconds = (
            total_handling_time_seconds / len(filtered_protocols)
            if len(filtered_protocols) > 0
            else 0
        )

        average_handling_time = timedelta(seconds=average_handling_time_seconds)

        # Atendente com mais atendimentos
        calls_per_attendant_distribution = {}
        for attendant in Attendant.objects.all():
            if attendant.name not in excluded_attendants:
                calls_count = Protocol.objects.filter(
                    attendant=attendant, start_date__year=year if year else today.year
                ).count()
                calls_per_attendant_distribution[attendant.name] = calls_count

        attendant_with_most_calls = max(
            calls_per_attendant_distribution, key=calls_per_attendant_distribution.get
        )

        # Atendente com menos atendimentos
        attendant_with_least_calls = min(
            calls_per_attendant_distribution, key=calls_per_attendant_distribution.get
        )

        return Response(
            {
                "average_handling_time": self.formatar_duracao(average_handling_time),
                "attendant_with_most_calls": attendant_with_most_calls,
                "attendant_with_least_calls": attendant_with_least_calls,
            }
        )
