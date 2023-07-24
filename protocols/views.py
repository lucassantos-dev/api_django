from .serializers import ProtocolSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Protocol
from attendants import models as modelsAttendant
import calendar
import locale

# Create your views here.
class ProtocolViewSet(viewsets.ModelViewSet):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer

# TOTAL DE ATENDIMENTOS MENSAL DO ANO
class CallsPerMonthView(APIView):
    def get(self, request):
        current_year = datetime.now().year
        protocols = Protocol.objects.all()
        monthly_counts = {}
        for protocol in protocols:
            start_date = datetime.strptime(protocol.start_date, "%d/%m/%Y %H:%M:%S")
            if start_date.year == current_year:
                month = start_date.month
                if month in monthly_counts:
                    monthly_counts[month] += 1
                else:
                    monthly_counts[month] = 1
        
        # Definir a localidade para português do Brasil (pt_BR)
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
        
        month_names_pt = [calendar.month_name[month].capitalize() for month in range(1, 13)]
        labels = [month_names_pt[month - 1] for month in range(1, 13) if month in monthly_counts.keys()]
        data = {
            'labels': labels,
            'counts': [monthly_counts[month] for month in range(1, 13) if month in monthly_counts.keys()]
        }

        return Response(data)
    
class MonthlyComparisonView(APIView):
    def post(self, request):
        if 'years' in request.data:
            years = request.data['years']
            if years == [] or type(years) != list:
                return Response('Erro', status='400')
            else:
                name = request.data.get('name', None)  # Obtém o valor do campo "name" da requisição
                # Filtra os protocolos com base nos anos e no nome (se fornecido)
                protocols = Protocol.objects.all()
                if name and name not in ['None', 'Todos']:
                    protocols = protocols.filter(name=name)
                # Dicionário para contar as ocorrências mensais
                monthly_counts = {}
                # Itera sobre os protocolos
                for protocol in protocols:
                    start_date = datetime.strptime(protocol.start_date, "%d/%m/%Y %H:%M:%S")
                    year = start_date.year
                    if year in years:
                        month = start_date.month
                        if year not in monthly_counts:
                            monthly_counts[year] = {}
                        if month in monthly_counts[year]:
                            monthly_counts[year][month] += 1
                        else:
                            monthly_counts[year][month] = 1

                # Configura o local para exibição dos nomes dos meses em português
                locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')

                # Obtém os nomes dos meses em português para uso nos rótulos
                month_names_pt = [calendar.month_name[month].capitalize() for month in range(1, 13)]
                labels = [month_names_pt[month - 1] for month in range(1, 13)]

                # Formata os dados no formato esperado pela resposta JSON
                data = []
                for year in years:
                    counts = [monthly_counts.get(int(year), {}).get(month, 0) for month in range(1, 13)]
                    data.append({
                        'year': int(year),
                        'counts': counts
                    })

                # Constrói a resposta com os rótulos e os dados formatados
                response_data = {
                    'labels': labels,
                    'data': data
                }
                return Response(response_data)
        else:
            return Response('Erro', status='400')


# MEDIA DE ATENDIMENTO DIARIO
class AverageDailyCallsView(APIView):
    def get(self,request):
        protocols = Protocol.objects.all()
        daily_counts = {}
        for protocol in protocols:
            start_date_str = protocol.start_date
            start_date = datetime.strptime(start_date_str, "%d/%m/%Y %H:%M:%S").date()
            if start_date in daily_counts:
                daily_counts[start_date] += 1
            else:
                daily_counts[start_date] = 1
        average_daily_calls = sum(daily_counts.values()) / len(daily_counts)
        return Response({'average_daily_calls': average_daily_calls})
    
# TOP PROTOCOLOS POR NOME DO CLIENTE
class TopNamesView(APIView):
    def get(self, request):
        top_names = Protocol.objects.values('name').annotate(count=Count('name')).order_by('-count')[:10]
        data = [{'labels': entry['name'], 'counts': entry['count']} for entry in top_names]
        return Response(data)

class NamesOrderView(APIView):
    def get(self, request):
        # Consulta os nomes e realiza a contagem de ocorrências com filtro
        top_names = (
            Protocol.objects.values('name')
            .annotate(count=Count('name'))
            .filter(count__gt=10)  # Filtro para contagem maior que 10
            .order_by('-count')
        )
        # Formata os dados no formato esperado pela resposta JSON
        data = [{'id': 0, 'name': 'Todos'}] + [{'id': idx, 'name': entry['name']} for idx, entry in enumerate(top_names, start=1)]
        # Retorna os dados como resposta JSON
        return Response(data)

# TOP PROTOCOLOS POR ATENDENTES
class ProtocolCountByAttendantView(APIView):
    def get(self, request):
        protocol_counts = (
            Protocol.objects
            .values('attendant__name')
            .annotate(count=Count('attendant__name'))
            .order_by('-count')
        )
        data = [{'labels': entry['attendant__name'], 'counts': entry['count']} for entry in protocol_counts]
        return Response(data)
    
# MEDIA DE ATENDIMENTOS POR ATENDENTE
class AverageCallsPerAttendantView(APIView):
    def get(self, request):
        attendants = modelsAttendant.Attendant.objects.all()
        average_calls = []

        for attendant in attendants:
            calls_count = Protocol.objects.filter(attendant=attendant).count()
            average_calls.append({
                'labels': attendant.name,
                'counts': calls_count
            })

        return Response(average_calls)
    
# TOP PROTOCOLOS POR DEPARTAMENTO
class ProtocolCountByDepartmentView(APIView):
    def get(self, request):
        protocol_counts = (
            Protocol.objects
            .values('department')
            .annotate(count=Count('department'))
            .order_by('-count')
        )
        data = [{'labels': entry['department'], 'counts': entry['count']} for entry in protocol_counts]
        return Response(data)
#--

# TOPS TAG  
class ProtocolCountByTagView(APIView):
    def get(self, request):
        protocol_counts = (
            Protocol.objects
            .values('tags')
            .annotate(tag_count=Count('tags'))
            .exclude(tags__in=['José Programador', 'nan'])
            .order_by('-tag_count')[:10]
        )
        data = []
        for entry in protocol_counts:
            tags = entry['tags'].split(',')
            for tag in tags:
                tag = tag.strip()
                if tag != 'nan':
                    data.append({'tag': tag, 'count': entry['tag_count']})
        return Response(data)
    
 # TOP TAGS POR MES   
class MonthlyTopTagView(APIView):

    def get(self, request):
        current_year = datetime.now().year
        protocols = Protocol.objects.all()
        monthly_top_tags = {}
        for protocol in protocols:
            start_date = datetime.strptime(protocol.start_date, "%d/%m/%Y %H:%M:%S")
            if start_date.year == current_year:
                month = start_date.month
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
            data[month] = {'top_tag': top_tag, 'count': tags[top_tag]}
        return Response(data)
    
# Tempo medio de espera    
class AverageWaitingTimeView(APIView):
    def get(self, request):
        protocols = Protocol.objects.all()
        filtered_protocols = protocols.exclude(waiting_time__gte='08:00:00').exclude(waiting_time='00:00:00')
        total_waiting_time = timedelta()
        count = 0

        for protocol in filtered_protocols:
            waiting_time = datetime.strptime(protocol.waiting_time, "%H:%M:%S")
            total_waiting_time += timedelta(hours=waiting_time.hour, minutes=waiting_time.minute, seconds=waiting_time.second)
            count += 1

        if count > 0:
            average_waiting_time = total_waiting_time / count
        else:
            average_waiting_time = timedelta()

        return Response({'average_waiting_time': str(average_waiting_time)})    
    
#tempo medio de espera por atendente 
class AverageWaitingTimeByAttendantView(APIView):
    def get(self, request):
        attendants = modelsAttendant.Attendant.objects.all()
        data = []

        for attendant in attendants:
            protocols = Protocol.objects.filter(attendant=attendant)
            filtered_protocols = protocols.exclude(waiting_time__gte='08:00:00').exclude(waiting_time='00:00:00')

            total_waiting_time = timedelta()
            count = 0

            for protocol in filtered_protocols:
                waiting_time = datetime.strptime(protocol.waiting_time, "%H:%M:%S")
                total_waiting_time += timedelta(hours=waiting_time.hour, minutes=waiting_time.minute, seconds=waiting_time.second)
                count += 1

            if count > 0:
                average_waiting_time = total_waiting_time / count
            else:
                average_waiting_time = timedelta()

            data.append({
                'attendant': attendant.name,
                'average_waiting_time': str(average_waiting_time)
            })

        return Response(data)
