from .serializers import ProtocolSerializer
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from datetime import datetime, timedelta
from .models import Protocol
from attendants import models as modelsAttendant

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
        data = {
            'labels': list(monthly_counts.keys()),
            'counts': list(monthly_counts.values())
        }

        return Response(data)
    
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
        data = [{'name': entry['name'], 'count': entry['count']} for entry in top_names]
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
        data = [{'attendant': entry['attendant__name'], 'count': entry['count']} for entry in protocol_counts]
        return Response(data)
    
# MEDIA DE ATENDIMENTOS POR ATENDENTE
class AverageCallsPerAttendantView(APIView):
    def get(self, request):
        attendants = modelsAttendant.Attendant.objects.all()
        average_calls = []

        for attendant in attendants:
            calls_count = Protocol.objects.filter(attendant=attendant).count()
            average_calls.append({
                'attendant': attendant.name,
                'average_calls': calls_count
            })

        return Response(average_calls)
    
#TOP PROTOCOLOS POR DEPARTAMENTO
class ProtocolCountByDepartmentView(APIView):
    def get(self, request):
        protocol_counts = (
            Protocol.objects
            .values('department')
            .annotate(count=Count('department'))
            .order_by('-count')
        )
        data = [{'department': entry['department'], 'count': entry['count']} for entry in protocol_counts]
        return Response(data)
#--

#TOPS TAG  
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
