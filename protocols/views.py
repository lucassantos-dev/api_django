from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Protocol
from attendants import models as modelsAttendant
import locale
from django.utils.translation import gettext as _
from collections import defaultdict
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils import timezone
from django.db.models import Avg,Count
from django.db.models.functions import TruncDate


# Dicionário que associa o número do mês ao nome do mês traduzido
MONTH_NAMES = {
    1: _('Jan'), 2: _('Fev'), 3: _('Mar'), 4: _('Abr'),
    5: _('Mai'), 6: _('Jun'), 7: _('Jul'), 8: _('Ago'),
    9: _('Set'), 10: _('Out'), 11: _('Nov'), 12: _('Dez'),
}

## CLIENTES #-- -- -- 
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
        # Obtém o ano atual usando o timezone-aware datetime
        current_year = timezone.now().year

        # Filtra os protocolos pelo ano atual
        protocols = Protocol.objects.filter(start_date__year=current_year)

        # Consulta para obter o número de protocolos criados em cada mês
        monthly_counts = protocols.annotate(
            month=ExtractMonth('start_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        # Monta a resposta JSON com os dados dos meses e contagens
        data = {
            'labels': [MONTH_NAMES[month] for month in range(1, 13)],
            'counts': [month['count'] for month in monthly_counts],
               }
        return Response(data)

class MonthlyComparisonView(APIView):
    """
    API View para comparar a contagem de protocolos por mês em anos específicos.

    Endpoint: /api/monthly-comparison/

    Requisição JSON:
    {
        "years": [year1, year2, ...],
        "name": "Nome do Protocolo" (opcional)
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
        if 'years' in data:
            years = data['years']
            if not isinstance(years, list) or not all(isinstance(year, int) for year in years):
                return Response('Erro', status=400)
            else:
                name = data.get('name', None)
                protocols = Protocol.objects.all()
                if name and name not in ['None', 'Todos']:
                    protocols = protocols.filter(name=name)
                # Contagem das ocorrências mensais no banco de dados
                monthly_counts = protocols.annotate(
                    year=ExtractYear('start_date'),
                    month=ExtractMonth('start_date')
                ).filter(year__in=years).values('year', 'month').annotate(
                    count=Count('id')
                ).order_by('year', 'month')
                # Configura o local para exibição dos nomes dos meses em português
                locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
                # Cria uma lista com os nomes dos meses em português (abreviados)
                month_names_pt_abbr = [_(datetime.strptime(str(month), '%m').strftime('%b')) for month in range(1, 13)]
                # Utiliza defaultdict para criar dicionário com valores padrão
                monthly_counts_dict = defaultdict(lambda: {month: 0 for month in range(1, 13)})
                for item in monthly_counts:
                    monthly_counts_dict[item['year']][item['month']] = item['count']
                # Formata os dados no formato esperado pela resposta JSON
                data = [{'year': year, 'counts': list(monthly_counts_dict[year].values())} for year in years]
                # Constrói a resposta com os rótulos e os dados formatados
                response_data = {'labels': month_names_pt_abbr, 'data': data}
                return Response(response_data)
        else:
            return Response('Erro', status=400)

class TopNamesView(APIView):
    """
    API View para obter os 10 nomes de protocolos mais frequentes.

    Endpoint: /api/top-names/

    Resposta JSON:
    [
        {"label": "Nome 1", "count": 10},
        {"label": "Nome 2", "count": 8},
        ...
    ]
    """
    def get(self, request):
        # Consulta para obter os 10 nomes de protocolos mais frequentes
        top_names = Protocol.objects.values('name').annotate(count=Count('name')).order_by('-count')[:10]
        
        # Formata os dados no formato esperado pela resposta JSON
        data = [{'labels': str(entry['name']), 'counts': entry['count']} for entry in top_names]
        
        # Retorna os dados formatados na resposta JSON
        return Response(data)

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
            Protocol.objects.values('name')
            .annotate(count=Count('name'))
            .filter(count__gt=10)  # Filtro para contagem maior que 10
            .order_by('-count')
        )
        
        # Formata os dados no formato esperado pela resposta JSON
        data = [{'id': 0, 'name': 'Todos'}] + [{'id': idx, 'name': str(entry['name'])} for idx, entry in enumerate(top_names, start=1)]
        
        # Retorna os dados como resposta JSON
        return Response(data)
    
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
    def get(self, request):
        # Obtém a data atual como um objeto datetime "aware" usando o fuso horário padrão
        today = timezone.now()
        # Filtra os protocolos do ano atual
        protocols_this_year = Protocol.objects.filter(start_date__year=today.year)
        # Calcula o número total de atendimentos do ano atual
        total_calls = protocols_this_year.count()
        # Filtra os protocolos com tempo de espera  que 08:00:00 e diferente de 00:00:00
        filtered_protocols = protocols_this_year.exclude(average_waiting_time__gte=timedelta(hours=4)).exclude(average_waiting_time=timedelta())
        # Calcula o tempo total de espera em segundos
        total_waiting_time_seconds = sum(protocol.average_waiting_time.total_seconds() for protocol in filtered_protocols)
        # Calcula o total de dias para a média diária de atendimentos
        start_dates_this_year = protocols_this_year.filter(start_date__lte=today).dates('start_date', 'day')
        total_days = (today.date() - min(start_dates_this_year)).days + 1
        # Calcula a média diária de atendimentos
        average_daily_calls = total_calls / total_days if total_days > 0 else 0
        # Calcula o tempo médio de espera
        average_waiting_time_seconds = total_waiting_time_seconds / len(filtered_protocols)
        average_waiting_time = timedelta(seconds=average_waiting_time_seconds)
        return Response({
            'total_calls': total_calls,
            'average_waiting_time': str(average_waiting_time)[:9],
            'average_daily_calls': round(average_daily_calls)
        })

    
## ATENDENTES --
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
        attendants = modelsAttendant.Attendant.objects.annotate(
            calls_count=Count('protocol', filter=TruncDate('protocol__start_date'))
        )

        average_calls = []

        # Calcula a média diária de atendimentos para cada atendente
        for attendant in attendants:
            total_days = Protocol.objects.filter(attendant=attendant).values('start_date__date').distinct().count()
            if total_days == 0:
                continue  # Para evitar divisão por zero, caso o atendente não tenha chamadas
            average_per_day = attendant.calls_count / total_days
            average_calls.append({
                'labels': attendant.name,
                'counts': round(average_per_day)  # Arredonda para 2 casas decimais
            })

        # Filtra os atendentes que você não deseja incluir na resposta
        attendants_to_remove = ["nan", "Programação", "Tax Protocolo"]
        average_calls = [entry for entry in average_calls if entry['labels'] not in attendants_to_remove]

        # Ordena os dados pelo valor da média (average) em ordem decrescente
        average_calls = sorted(average_calls, key=lambda x: x['counts'], reverse=True)

        return Response(average_calls)
            
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

class ProtocolCountByTagView(APIView):
    """
    API View para obter a contagem de protocolos por tag.

    Endpoint: /api/protocol-count-by-tag/

    Resposta JSON:
    [
        {"tag": "Tag 1", "count": 10},
        {"tag": "Tag 2", "count": 8},
        ...
    ]
    """
    def get(self, request):
        # Consulta a contagem de protocolos por tag
        protocol_counts = (
            Protocol.objects
            .values('tags')
            .annotate(tag_count=Count('tags'))
            .exclude(tags__in=['José Programador', 'nan'])
            .order_by('-tag_count')[:10]
        )
        
        # Formata os dados no formato esperado pela resposta JSON
        data = []
        for entry in protocol_counts:
            tags = entry['tags'].split(',')
            for tag in tags:
                tag = tag.strip()
                if tag != 'nan':
                    data.append({'labels': tag, 'counts': entry['tag_count']})
        
        # Retorna os dados como resposta JSON
        return Response(data)  

class MonthlyTopTagView(APIView):
    """
    API View para obter a tag mais frequente por mês no ano atual.

    Endpoint: /api/monthly-top-tag/

    Resposta JSON:
    {
        "month1": {"top_tag": "Tag 1", "count": 10},
        "month2": {"top_tag": "Tag 2", "count": 8},
        ...
    }
    """
    def get(self, request):
        current_year = datetime.now().year
        
        # Consulta apenas os protocolos do ano atual
        protocols = Protocol.objects.filter(start_date__year=current_year)
        
        monthly_top_tags = {}
        
        for protocol in protocols:
            month = protocol.start_date.month
            tags = protocol.tags.split(',')
            for tag in tags:
                tag = tag.strip()
                if tag != 'nan':
                    if month not in monthly_top_tags:
                        monthly_top_tags[month] = {}
                    if tag not in monthly_top_tags[month]:
                        monthly_top_tags[month][tag] = 1
                    else:
                        monthly_top_tags[month][tag] += 1
        
        data = {}
        
        for month, tags in monthly_top_tags.items():
            top_tag = max(tags, key=tags.get)
            data[month] = {'labels': top_tag, 'counts': tags[top_tag]}
        
        # Retorna os dados como resposta JSON
        return Response(data)

class AverageTimeByAttendantView(APIView):
    """
    API View para obter o tempo médio de atendimento por atendente.

    Endpoint: /api/average-time-by-attendant/

    Resposta JSON:
    [
        {"attendant": "Atendente 1", "average_time": "02:30:00"},
        {"attendant": "Atendente 2", "average_time": "01:45:00"},
        ...
    ]
    """
    def get(self, request):
        attendants = modelsAttendant.Attendant.objects.all()
        data = []
        for attendant in attendants:
            protocols = Protocol.objects.filter(attendant=attendant)
            # Filtra os protocolos com tempo de espera não igual a '08:00:00' ou '00:00:00'
            filtered_protocols = protocols.exclude(total_attendance_time__gte=timedelta(hours=8)).exclude(total_attendance_time=timedelta())

            # Calcula o tempo médio de espera
            total_attendance_time = filtered_protocols.aggregate(avg_time=Avg('total_attendance_time'))['avg_time'] or timedelta()

            data.append({
                'labels': attendant.name,
                'counts': str(total_attendance_time)
            })

        return Response(data)
    
