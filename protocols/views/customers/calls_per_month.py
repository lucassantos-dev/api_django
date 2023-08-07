from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
import locale
from django.utils.translation import gettext as _
from collections import defaultdict
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Count
from django.utils import timezone
from attendants.models import Attendant

# Dicionário que associa o número do mês ao nome do mês traduzido
MONTH_NAMES = {
    1: _("Jan"),
    2: _("Fev"),
    3: _("Mar"),
    4: _("Abr"),
    5: _("Mai"),
    6: _("Jun"),
    7: _("Jul"),
    8: _("Ago"),
    9: _("Set"),
    10: _("Out"),
    11: _("Nov"),
    12: _("Dez"),
}


class MonthlyComparisonView(APIView):
    """
    API View para comparar a contagem de protocolos por mês em anos específicos.
    Endpoint: /api/monthly-comparison/
    Requisição JSON:
    {
        "years": [year1, year2, ...],
        "names": ["Nome do Protocolo 1", "Nome do Protocolo 2"] (opcional)
    }
    Resposta JSON:
    {
        "labels": ["Jan", "Fev", ..., "Dez"],
        "data": [
            {"year": year1, "counts": [count_jan, count_fev, ..., count_dez]},
            {"year": year2, "counts": [count_jan, count_fev, ..., count_dez]},
            ...
        ]
    }
    """

    def post(self, request):
        data = request.data
        years = data.get("years", [])
        names = data.get("names", [])

        if not isinstance(years, list) or not all(
            isinstance(year, int) for year in years
        ):
            return Response(
                "Erro: Os anos devem ser fornecidos em uma lista válida.", status=400
            )

        if not isinstance(names, list):
            names = [names]

        if names and any(name in ["None", "Todos"] for name in names):
            return Response("Erro: Nomes inválidos fornecidos na lista.", status=400)

        protocols = Protocol.objects.all()
        tax_protocolo_attendant = Attendant.objects.get(name="Tax Protocolo")
        programacao_attendant = Attendant.objects.get(name="Programação")
        protocols = protocols.exclude(attendant=tax_protocolo_attendant)
        protocols = protocols.exclude(attendant=programacao_attendant)
        if names:
            protocols = protocols.filter(name__in=names)

        monthly_counts = (
            protocols.annotate(
                year=ExtractYear("start_date"), month=ExtractMonth("start_date")
            )
            .filter(year__in=years)
            .values("year", "month")
            .annotate(count=Count("id"))
            .order_by("year", "month")
        )

        # Configura o local para exibição dos nomes dos meses em português
        locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
        # Cria uma lista com os nomes dos meses em português (abreviados)
        month_names_pt_abbr = [MONTH_NAMES[month] for month in range(1, 13)]
        # Utiliza default_dict para criar dicionário com valores padrão
        monthly_counts_dict = defaultdict(lambda: {month: 0 for month in range(1, 13)})
        for item in monthly_counts:
            monthly_counts_dict[item["year"]][item["month"]] = item["count"]
        # Formata os dados no formato esperado pela resposta JSON
        data = [
            {"year": year, "counts": list(monthly_counts_dict[year].values())}
            for year in years
        ]
        # Constrói a resposta com os rótulos e os dados formatados
        response_data = {"labels": month_names_pt_abbr, "data": data}
        return Response(response_data)


class CallsPerMonthView(APIView):
    """
    API View para obter o número de protocolos criados em cada mês do ano atual.

    Endpoint: /api/calls-per-month/

    Resposta JSON:
    {
        "labels": ["Jan", "Fev", ..., "Dez"],
        "counts": [count_jan, count_fev, ..., count_dez]
    }
    """

    def get(self, request):
        # Obtém o ano atual usando o timezone
        current_year = timezone.now().year
        protocols = Protocol.objects.filter(start_date__year=current_year)

        tax_protocolo_attendant = Attendant.objects.get(name="Tax Protocolo")
        programacao_attendant = Attendant.objects.get(name="Programação")
        protocols = protocols.exclude(attendant=tax_protocolo_attendant)
        protocols = protocols.exclude(attendant=programacao_attendant)
        # Filtra os protocolos pelo ano atual

        # Consulta para obter o número de protocolos criados em cada mês
        monthly_counts = (
            protocols.annotate(month=ExtractMonth("start_date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        # Monta a resposta JSON com os dados dos meses e contagens
        data = {
            "labels": [MONTH_NAMES[month] for month in range(1, 13)],
            "counts": [month["count"] for month in monthly_counts],
        }
        return Response(data)
