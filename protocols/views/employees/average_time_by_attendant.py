from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import Protocol
from django.utils.translation import gettext as _
from attendants.models import Attendant
from django.db.models import Avg
from datetime import timedelta


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
        attendants = Attendant.objects.all()
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