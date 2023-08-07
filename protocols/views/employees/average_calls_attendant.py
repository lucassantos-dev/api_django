from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
from django.utils.translation import gettext as _
from django.db.models import Count
from django.db.models.functions import TruncDate
from attendants.models import Attendant


class AverageCallsPerAttendantView(APIView):
    """
    API View para obter a média diária de atendimentos por atendente.

    Endpoint: /api/average-calls-per-attendant/

    Resposta JSON:
    [
        {"label": "Atendente 1", "average": 10.5},
        {"label": "Atendente 2", "average": 8.0},
        ...
    ]
    """

    def get(self, request):
        # Consulta todos os atendentes com a contagem de chamadas por dia
        attendants = Attendant.objects.annotate(
            calls_count=Count("protocol", filter=TruncDate("protocol__start_date"))
        )
        average_calls = []
        # Calcula a média diária de atendimentos para cada atendente
        for attendant in attendants:
            total_days = (
                Protocol.objects.filter(attendant=attendant)
                .values("start_date__date")
                .distinct()
                .count()
            )
            if total_days == 0:
                continue  # Para evitar divisão por zero, caso o atendente não tenha chamadas
            average_per_day = attendant.calls_count / total_days
            average_calls.append(
                {
                    "labels": attendant.name,
                    "counts": round(average_per_day),  # Arredonda para 2 casas decimais
                }
            )

        # Filtra os atendentes que você não deseja incluir na resposta
        attendants_to_remove = ["nan", "Programação", "Tax protocolo"]
        average_calls = [
            entry
            for entry in average_calls
            if entry["labels"] not in attendants_to_remove
        ]

        # Ordena os dados pelo valor da média (average) em ordem decrescente
        average_calls = sorted(average_calls, key=lambda x: x["counts"], reverse=True)

        return Response(average_calls)
