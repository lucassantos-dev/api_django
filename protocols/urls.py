from django.urls import path
from .views import (CallsPerMonthView,AverageDailyCallsView, 
                    TopNamesView,ProtocolCountByAttendantView,
                    ProtocolCountByDepartmentView, ProtocolCountByTagView,
                    MonthlyTopTagView, AverageWaitingTimeView,
                    AverageWaitingTimeByAttendantView)

urlpatterns = [
    # ... outras URLs ...
    path('calls-per-month/', CallsPerMonthView.as_view(), 
         name='calls-per-month'),
    path('average-daily-calls/', AverageDailyCallsView.as_view(), 
         name='average-daily-calls'),
    path('top-names/', TopNamesView.as_view(), 
         name='top-names'),
    path('protocol-by-attendant/', ProtocolCountByAttendantView.as_view(), 
         name='protocol-by-attendant'),
    path('protocol-by-department/', ProtocolCountByDepartmentView.as_view(), 
         name='protocol-by-department'),
    path('protocol-by-tag/', ProtocolCountByTagView.as_view(), 
         name='protocol-by-tag'),
    path('protocol-top-tag-moth/', MonthlyTopTagView.as_view(), 
         name='protocol-top-tag-moth'),
    path('average-waiting-time/', AverageWaitingTimeView.as_view(), 
         name='average-waiting-time'),
    path('average-waiting-time-attendant/', AverageWaitingTimeByAttendantView.as_view(), 
         name='average-waiting-time-attendant'),
]
