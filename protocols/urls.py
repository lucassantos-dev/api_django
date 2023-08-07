from django.urls import path
from .views.customers import calls_per_month, companies_name, names_per_year, statistics
from .views.employees import (
    average_calls_attendant,
    average_time_by_attendant,
    protocol_by_attendant,
    protocol_by_department,
    statistics as em_statistics,
)

urlpatterns = [
    path(
        "calls-per-month/",
        calls_per_month.CallsPerMonthView.as_view(),
        name="calls-per-month",
    ),
    path(
        "monthly-comparison/",
        calls_per_month.MonthlyComparisonView.as_view(),
        name="monthly-comparison",
    ),
    path("top-names/", names_per_year.TopNamesView.as_view(), name="top-names"),
    path("names-order/", companies_name.NamesOrderView.as_view(), name="names-order"),
    path(
        "average-calls-per-attendant/",
        average_calls_attendant.AverageCallsPerAttendantView.as_view(),
        name="average-calls-per-attendant-view",
    ),
    path(
        "protocol-by-attendant/",
        protocol_by_attendant.ProtocolCountByAttendantView.as_view(),
        name="protocol-by-attendant",
    ),
    path(
        "protocol-by-department/",
        protocol_by_department.ProtocolCountByDepartmentView.as_view(),
        name="protocol-by-department",
    ),
    path(
        "average-time-attendant/",
        average_time_by_attendant.AverageTimeByAttendantView.as_view(),
        name="average-time-attendant",
    ),
    path("statistics/", statistics.ProtocolStatisticsView.as_view(), name="statistics"),
    path(
        "employees_statistics/",
        em_statistics.AttendantStatisticsView.as_view(),
        name="employees_statistics",
    ),
]
