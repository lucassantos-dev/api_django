from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
from django.utils.translation import gettext as _
from django.db.models import Count


class NamesOrderView(APIView):

    """
    API View para obter os nomes de protocolos com contagem maior que 10 ordenados por ocorrências.

    Endpoint: /api/names-order/
    Resposta JSON:
    [
        {"id": 0, "name": "Todos"},
        {"id": 1, "name": "Nome 1"},
        {"id": 2, "name": "Nome 2"},
        ...
    ]
    """

    def get(self, request):
        # Consulta os nomes e realiza a contagem de ocorrências com filtro

        top_names = (
            Protocol.objects.values("name")
            .annotate(count=Count("name"))
            .filter(count__gt=10)  # Filtro para contagem maior que 10
            .order_by("-count")
        )
        data = [{"id": 0, "name": "Todos"}] + [
            {"id": idx, "name": str(entry["name"])}
            for idx, entry in enumerate(top_names, start=1)
        ]
        # Retorna os dados como resposta JSON
        return Response(data)
