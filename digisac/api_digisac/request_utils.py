import os
import requests
from datetime import datetime
import json

class DigisacConfigRequest:
    
    def __init__(self):
        self.url = os.getenv('URL_API_DIGISAC')
        self.token = os.getenv('TOKEN_API_DIGISAC')
 
    def convert_dates_format(self, date_str1, date_str2):
        try:
            # Converter as datas de string para objetos de data
            date_obj1 = datetime.strptime(date_str1, "%d/%m/%Y")
            date_obj2 = datetime.strptime(date_str2, "%d/%m/%Y")
            # Converter as datas para o formato desejado
            formatted_date1 = date_obj1.strftime("%Y-%m-%dT00:00:00.000Z")
            formatted_date2 = date_obj2.strftime("%Y-%m-%dT23:59:59.999Z")
            return formatted_date1, formatted_date2
        except ValueError:
            print("Formato de data inválido. Certifique-se de usar o formato dd/mm/aaaa.")
            return None, None

    def get_historic(self, start_period=None, end_period=None):
        try:
            if not start_period and not end_period:
              start_period = '01/01/1999'
              end_period = '31/12/2050'
            start_period, end_period = self.convert_dates_format(start_period, end_period)
            headers = {}
            query_params = {
                "distinct": True,
                "order": [["updatedAt", "DESC"]],
                "where": {
                    "$or": {
                        "startedAt": {
                            "$gte": f"{start_period}",
                            "$lte": f"{end_period}"
                        },
                        "endedAt": {
                            "$gte": f"{start_period}",
                            "$lte": f"{end_period}"
                        }
                    }
                },
                "include": [
                    {"model": "account"},
                    {"model": "firstMessage", "attributes": ["id", "type", "text", "timestamp", "isFromMe", "sent", "data",
                     "accountId", "serviceId", "contactId", "fromId", "toId",
                     "userId", "ticketId", "isFromBot", "isFromSync", "visible", "ticketUserId", "ticketDepartmentId",
                     "origin", "botId", "campaignId"]},
                    {"model": "contact", "attributes": ["id", "accountId", "name", "alternativeName", "internalName", "serviceId", 
                        "data", "note", "personId", "status"], "required": True,
                    "where": {"visible": True}, "include": [{"model": "service", "attributes": ["id", "name", "type",
                    "accountId", "botId", "archivedAt"], "required": True}, 
                    {"model": "tags", "attributes": ["id", "label", "accountId"]},
                    {"model": "person", "attributes": ["id", "name", "document", "accountId"]}, {"model": "thumbAvatar"}]},
                    {"model": "user", "attributes": ["id", "name", "email", "isSuperAdmin", "active", "accountId", 
                        "isFirstLogin", "status", "timetableId", "archivedAt", "phoneNumber", "data", "language", "isActiveInternalChat"]},
                    {"model": "department", "attributes": ["id", "name", "accountId", "archivedAt", "distributionId"]},
                    {"model": "ticketTopics", "attributes": ["id", "name", "archivedAt"]}
                ],
                "page": 1,
                "perPage": 1000
            }
            query_json = json.dumps(query_params)
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
            response = requests.get(f"{self.url}/tickets", headers=headers, params={"query": query_json})
            response.raise_for_status()
            all_results = []
            while True:
                response = requests.get(f"{self.url}/tickets", headers=headers, params={"query": query_json})
                response.raise_for_status()
                data = response.json()
                all_results.extend(data['data'])
                if len(data['data']) < 1000: 
                    break
                query_params["page"] += 1
                query_json = json.dumps(query_params)
            return all_results
        except requests.RequestException as e:
            print('Erro na requisição:', e)
            return None

    def get_attendants(self, user_id):
      try:
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        response = requests.get(f"{self.url}/tickets", headers=headers, params={"userId": user_id})
        response.raise_for_status()
        return response.json()
      except requests.RequestException as e:
        print('Erro na requisição:', e)
        return None
    