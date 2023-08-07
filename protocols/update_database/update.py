from ..models import Protocol
from attendants.models import Attendant
from django.utils import timezone
from datetime import datetime, timedelta, time
import holidays
from django.utils.timezone import make_aware
from tqdm import tqdm


def is_business_day_and_hours(date_to_check):
    try:
        if date_to_check.weekday() >= 5:
            return False

        br_holidays = holidays.Brazil(state="CE")
        if date_to_check in br_holidays:
            return False

        horario_inicio_manha = time(8, 0)
        horario_fim_manha = time(12, 0)
        horario_inicio_tarde = time(13, 15)
        horario_fim_tarde = time(18, 0)

        if (horario_inicio_manha <= date_to_check.time() <= horario_fim_manha) or (
            horario_inicio_tarde <= date_to_check.time() <= horario_fim_tarde
        ):
            return True
        else:
            return False
    except ValueError:
        print(
            "Formato de data ou hora inválido. Certifique-se de usar o formato correto."
        )
        return False


def create_protocol(data_json):
    start_date = timezone.datetime.strptime(
        data_json["startedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    start_date = make_aware(start_date)
    is_business_day = is_business_day_and_hours(start_date)
    protocol_number = data_json["protocol"]
    if Protocol.objects.filter(protocol_number=protocol_number).exists():
        return

    attendant_name = "S/A"
    if data_json["user"]:
        attendant_name = data_json["user"]["name"]

    limit_period = datetime.strptime("27/03/2023", "%d/%m/%Y")
    limit_period = make_aware(limit_period)
    if start_date < limit_period and attendant_name == "Fran Araujo":
        attendant_name = "Victoria"

    attendant, _ = Attendant.objects.get_or_create(name=attendant_name)

    if data_json["account"]["name"] == "Tax":
        return
    name = str(data_json["contact"]["name"]).capitalize()
    number = None
    if data_json["contact"]["data"]["number"]:
        number = data_json["contact"]["data"]["number"]
    tags = data_json["ticketTopics"]
    department = "S/D"
    if data_json["department"]:
        department = data_json["department"]["name"]

    # --
    total_attendance_time = data_json["metrics"].get("ticketTime")
    total_attendance_time = (
        timedelta(seconds=total_attendance_time) if total_attendance_time else None
    )
    # --
    first_waiting_time = data_json["metrics"].get("waitingTime")
    first_waiting_time = (
        timedelta(seconds=first_waiting_time) if first_waiting_time else None
    )
    # --
    average_waiting_time = data_json["metrics"].get("waitingTimeTransfersAvg")
    average_waiting_time = (
        timedelta(seconds=average_waiting_time) if average_waiting_time else None
    )
    # --
    call_type = data_json["origin"]
    try:
        is_from_me = data_json["firstMessage"]["isFromMe"]
    except:
        is_from_me = None
    protocol = Protocol(
        protocol_number=protocol_number,
        name=name,
        number=number,
        attendant=attendant,
        tags=tags,
        department=department,
        start_date=start_date,
        total_attendance_time=total_attendance_time,
        first_waiting_time=first_waiting_time,
        average_waiting_time=average_waiting_time,
        call_type=call_type,
        is_business_hours=is_business_day,
        is_from_me=is_from_me,
    )
    protocol.save()


def update(data):
    for data_json in tqdm(data):
        create_protocol(data_json)
