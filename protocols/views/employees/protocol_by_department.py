from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
from django.utils.translation import gettext as _
from django.db.models import Count

class ProtocolCountByDepartmentView(APIView): 
    """
    API View para obter a contagem de protocolos por departamento.

    Endpoint: /api/protocol-count-by-department/

    Resposta JSON:
    [
        {"label": "Departamento 1", "count": 10},
        {"label": "Departamento 2", "count": 8},
        ...
    ]
    """
    def get(self, request):
        # Consulta a contagem de protocolos por departamento
        protocol_counts = (
            Protocol.objects
            .values('department')
            .annotate(count=Count('department'))
            .order_by('-count')
        )
        
        # Formata os dados no formato esperado pela resposta JSON
        data = [{'labels': entry['department'], 'counts': entry['count']} for entry in protocol_counts]
        
        # Retorna os dados como resposta JSON
        return Response(data)