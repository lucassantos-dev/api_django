from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
from django.db.models.functions import ExtractYear
from django.db.models import Count


class TopNamesView(APIView):
    """
    API View para obter os 10 nomes de protocolos mais frequentes.
    Endpoint: /api/top-names/
    Requisição JSON (opcional):
    {
        "year": 2023
    }
    Resposta JSON:
    [
        {"label": "Nome 1", "count": 10},
        {"label": "Nome 2", "count": 8},
        ...
    ]
    """

    def post(self, request):
        data = request.data
        year = data.get("year", None)

        protocols = Protocol.objects.all()

        # Filtra os protocolos pelo ano, se o filtro for fornecido
        if year and isinstance(year, int):
            protocols = protocols.filter(start_date__year=year)

        # Consulta para obter os 10 nomes de protocolos mais frequentes
        top_names = (
            protocols.values("name")
            .annotate(count=Count("name"))
            .order_by("-count")[:10]
        )

        # Formata os dados no formato esperado pela resposta JSON
        data = [
            {"labels": entry["name"], "counts": entry["count"]} for entry in top_names
        ]
        # Retorna os dados formatados na resposta JSON
        return Response(data)
