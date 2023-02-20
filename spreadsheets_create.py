# Подключаем библиотеки
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from env_reader import config

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(config.credentials_file,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API

spreadsheet = service.spreadsheets().create(body={
    'properties': {'title': 'Первый тестовый документ', 'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист номер один',
                               'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
}).execute()
spreadsheetId = spreadsheet['spreadsheetId']  # сохраняем идентификатор файла
print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)

driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)  # Выбираем работу с Google Drive и 3 версию API
access = driveService.permissions().create(
    fileId=spreadsheetId,
    body={'type': 'user', 'role': 'writer', 'emailAddress': config.my_email},
    # Открываем доступ на редактирование
    fields='id'
).execute()
