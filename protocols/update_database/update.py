import os
import pandas as pd
from datetime import datetime
from ..models import  Protocol
from attendants.models import Attendant
from django.conf import settings
# from celery import shared_task


# @shared_task
def update():
    try:
        DOWNLOAD_FOLDER = settings.DOWNLOAD_FOLDER
        files = os.listdir(DOWNLOAD_FOLDER)
        for file_name in files:
            file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
            if os.path.isfile(file_path):
                df = pd.read_csv(file_path, sep=";", dtype=str)
                for _, row in df.iterrows():
                    attendant_name = row["Atendente"]
                    initial_date = datetime.strptime(
                        row["Data de início"], "%d/%m/%Y %H:%M:%S"
                    )
                    limit_period = datetime.strptime("27/03/2023", "%d/%m/%Y")

                    if initial_date < limit_period and attendant_name == "Fran Araujo":
                        attendant_name = "Victoria"

                    try:
                        attendant = Attendant.objects.get(name=attendant_name)
                    except Attendant.DoesNotExist:
                        # Attendant does not exist, create a new instance
                        attendant = Attendant.objects.create(name=attendant_name)

                    try:
                        protocol = Protocol.objects.get(
                            number_protocol=row["Protocolo"]
                        )
                    except Protocol.DoesNotExist:
                        protocol = Protocol.objects.create(
                            number=row["Número"],
                            name=row["Nome"],
                            attendant=attendant,
                            department=row["Departamento"],
                            start_date=row["Data de início"],
                            end_date=row["Data de encerramento"],
                            handling_time=row["Tempo total de atendimento"],
                            waiting_time=row["1º tempo de espera"],
                            average_waiting_time=row["Tempo médio de espera"],
                            protocol_type=row["Tipo (Receptivo/Ativo)"],
                            number_protocol=row["Protocolo"],
                            tags=row["Tags"],
                        )

        return True
    except Exception as e:
        error_message = "Erro no insert do banco"
        print(f"{error_message}: {e}")
        return False