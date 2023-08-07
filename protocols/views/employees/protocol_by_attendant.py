from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
from django.utils.translation import gettext as _
from django.db.models import Count

class ProtocolCountByAttendantView(APIView):
    """
    API View para obter a contagem de protocolos por atendente.

    Endpoint: /api/protocol-count-by-attendant/

    Resposta JSON:
    [
        {"label": "Atendente 1", "count": 10},
        {"label": "Atendente 2", "count": 8},
        ...
    ]
    """
    def get(self, request):
        # Consulta a contagem de protocolos por atendente
        protocol_counts = (
            Protocol.objects
            .values('attendant__name')
            .annotate(count=Count('attendant__name'))
            .order_by('-count')
        )
        attendants_to_remove = ["nan", "Programação", "Tax Protocolo"]
        protocol_counts = [entry for entry in protocol_counts if entry['attendant__name'] not in attendants_to_remove]
        # Formata os dados no formato esperado pela resposta JSON
        data = [{'labels': entry['attendant__name'], 'counts': entry['count']} for entry in protocol_counts]
        # Retorna os dados como resposta JSON
        return Response(data)