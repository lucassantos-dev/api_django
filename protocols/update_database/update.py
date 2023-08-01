import os
import pandas as pd
from ..models import  Protocol
from attendants.models import Attendant
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta, time

def adjust_time_limit(duration):
    max_duration = timedelta(hours=8)
    return min(duration, max_duration)

def is_business_day_and_hours(date_to_check):
    try:
        data_hora = datetime.strptime(date_to_check, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Verificar se é um dia útil (segunda a sexta, onde 0 é segunda-feira e 4 é sexta-feira)
        if data_hora.weekday() >= 5:
            return False

        # Definir os horários de início e fim do horário comercial
        horario_inicio_manha = time(8, 0)
        horario_fim_manha = time(12, 0)
        horario_inicio_tarde = time(13, 15)
        horario_fim_tarde = time(18, 0)

        # Verificar se a data e hora estão dentro do horário comercial
        if (horario_inicio_manha <= data_hora.time() <= horario_fim_manha) or (horario_inicio_tarde <= data_hora.time() <= horario_fim_tarde):
            return True
        else:
            return False

    except ValueError:
        print("Formato de data ou hora inválido. Certifique-se de usar o formato correto.")
        return False


def update(data):
    try:
        for data_json in data:
            is_business_day = is_business_day_and_hours(data_json['startedAt'])
            pass             
    except:
        pass

    #                 protocol_number = row['Protocolo']
    #                 if Protocol.objects.filter(protocol_number=protocol_number).exists():
    #                     # Registro já existe, pule para o próximo
    #                     continue
    #                 attendant_name = row['Atendente']
    #                 limit_period = datetime.strptime("27/03/2023", "%d/%m/%Y")
    #                 start_date = timezone.datetime.strptime(row['Data de início'],  '%d/%m/%Y %H:%M:%S')
    #                 if start_date < limit_period and attendant_name == "Fran Araujo":
    #                     attendant_name = "Victoria"
    #                 attendant, _ = Attendant.objects.get_or_create(name=attendant_name)
    #                 # Verificar se a conexão é 'Tax' e pular a criação do protocolo nesse caso
    #                 if row['Conexão'] == 'Tax':
    #                     continue
    #                 name = row['Nome']
    #                 number = row['Número']
    #                 tags = row['Tags']
    #                 department = row['Departamento']
    #                 total_attendance_time_str = row['Tempo total de atendimento']
    #                 total_attendance_time = timedelta(seconds=int(total_attendance_time_str.split(':')[0]) * 3600 + int(total_attendance_time_str.split(':')[1]) * 60 + int(total_attendance_time_str.split(':')[2])) if total_attendance_time_str else None
    #                 total_attendance_time = adjust_time_limit(total_attendance_time)
    #                 first_waiting_time_str = row['1º tempo de espera']
    #                 first_waiting_time = timedelta(seconds=int(first_waiting_time_str.split(':')[0]) * 3600 + int(first_waiting_time_str.split(':')[1]) * 60 + int(first_waiting_time_str.split(':')[2])) if first_waiting_time_str else None
    #                 first_waiting_time = adjust_time_limit(first_waiting_time)
    #                 average_waiting_time_str = row['Tempo médio de espera']
    #                 average_waiting_time = timedelta(seconds=int(average_waiting_time_str.split(':')[0]) * 3600 + int(average_waiting_time_str.split(':')[1]) * 60 + int(average_waiting_time_str.split(':')[2])) if average_waiting_time_str else None
    #                 average_waiting_time = adjust_time_limit(average_waiting_time)
    #                 call_type = row['Tipo (Receptivo/Ativo)']
    #                 # Adicionando informações de fuso horário ao objeto start_date
    #                 start_date = timezone.make_aware(start_date)

    #                 protocol = Protocol(
    #                     protocol_number=protocol_number,
    #                     name=name,
    #                     number=number,
    #                     attendant=attendant,
    #                     tags=tags,
    #                     department=department,
    #                     start_date=start_date,
    #                     total_attendance_time=total_attendance_time,
    #                     first_waiting_time=first_waiting_time,
    #                     average_waiting_time=average_waiting_time,
    #                     call_type=call_type,)
    #                 protocol.save()
    #     return True
    # except Exception as e:
    #     error_message = "Erro no insert do banco"
    #     print(f"{error_message}: {e}")
    #     return False