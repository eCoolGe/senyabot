from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import apiclient
from env_reader import config
from config import SURNAME_RANGES, DATE_RANGES, LOG_RANGES, PAY_RANGES
import utils

SPREADSHEET_ID = config.spreadsheet_id
ABC = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
       "w", "x", "y", "z", "aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai", "aj", "ak", "al", "am", "an", "ao",
       "ap", "aq", "ar", "as", "at", "au", "av", "aw", "ax", "ay", "az", "ba", "bb", "bc", "bd", "be", "bf", "bg",
       "bh", "bi", "bj", "bk", "bl", "bm", "bn", "bo", "bp", "bq", "br", "bs", "bt", "bu", "bv", "bw", "bx", "by", "bz"]

# Читаем ключи из файла с закрытым ключом
credentials = ServiceAccountCredentials.from_json_keyfile_name(config.credentials_file,
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API


def get_data(spreadsheet_id, ranges, major_dimension='ROWS'):
    """
    Получает данные из таблицы по заданному диапазону
    """
    data_results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id,
                                                            ranges=ranges,
                                                            valueRenderOption='FORMATTED_VALUE',
                                                            dateTimeRenderOption='FORMATTED_STRING',
                                                            majorDimension=major_dimension).execute()
    return data_results['valueRanges'][0]['values']


def get_index(value, spreadsheet_id, list_name, ranges, major_dimension='ROWS'):
    """
    Ищет заданное значение в диапазоне, если находит - возвращает индекс, если нет -
    создает эти данные и возвращает их индекс
    """
    sheet_values = get_data(spreadsheet_id, ranges, major_dimension)

    try:
        index = sheet_values.index([value])
    except ValueError:
        index = len(sheet_values)

        if major_dimension == "ROWS":
            range_str = f"{list_name}!B{index + 1}"
        else:
            range_str = f"{list_name}!{ABC[index]}2"

        service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
            "valueInputOption": "USER_ENTERED",
            "data": [{
                "range": range_str,
                "majorDimension": "ROWS",
                "values": [[f"{value}"]]
            }]
        }).execute()
    return index


def upload_list_pay(horizontal_name, vertical_name, external_pay, list_name):
    """
    Обновляет определенную ячейку по алгоритму шахматной доски - сначала находит горизонтальный индекс,
    потом вертикальный, скрещенное значение - обновляет
    """
    horizontal = [f"{list_name}!{SURNAME_RANGES}"]
    vertical = [f"{list_name}!{DATE_RANGES}"]

    first_index = ABC[get_index(horizontal_name, SPREADSHEET_ID, list_name, horizontal, 'COLUMNS')]
    last_index = get_index(vertical_name, SPREADSHEET_ID, list_name, vertical) + 1

    try:
        internal_pay = get_data(SPREADSHEET_ID, f"{list_name}!{first_index}{last_index}")
        internal_pay = internal_pay[0][0]
    except KeyError:
        internal_pay = 0

    pay = int(external_pay) + int(internal_pay)
    print(pay)

    service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={
        "valueInputOption": "USER_ENTERED",
        "data": [{
            "range": f"{list_name}!{first_index}{last_index}",
            "majorDimension": "ROWS",
            "values": [[f"{pay}"]]
        }]
    }).execute()


def upload_log_message(list_name, log_text):
    """
    Записывает полученное сообщение в лог сообщений, разбивая его на основные части
    """
    sheet_values = get_data(SPREADSHEET_ID, LOG_RANGES[0])
    last_index = len(sheet_values) + 1

    if len(log_text) == 4:
        values = [utils.today(), log_text[0], log_text[1], log_text[2], log_text[3]]
    else:
        values = [utils.today(), log_text[0], log_text[1], log_text[2], log_text[3], log_text[4]]

    service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": f"{list_name}!{LOG_RANGES[1]}{last_index}:{LOG_RANGES[2]}{last_index}",
             "majorDimension": "ROWS",
             "values": [
                 values
             ]}
        ]
    }).execute()


def pay_calculate(list_name, date_calculate):
    """
    Возвращает массив строковых элементов типа "Имя - Сумма" или же сообщение о том, что таких данных нет
    """
    try:
        result = []
        result_sum = 0

        date_index = get_data(SPREADSHEET_ID, f"{list_name}!{DATE_RANGES}").index([date_calculate]) + 1
        sheet_values = get_data(SPREADSHEET_ID, f"{list_name}!{PAY_RANGES[0]}{date_index}:{PAY_RANGES[1]}{date_index}",
                                'COLUMNS')
        iteration_index = 2  # ABC[2] = C
        for sheet_value in sheet_values:
            if sheet_value:
                get_surname = get_data(SPREADSHEET_ID, f"{list_name}!{ABC[iteration_index]}{PAY_RANGES[2]}")
                result.append(f"{get_surname[0][0]} — {sheet_value[0]}")
                result_sum += int(sheet_value[0])
            iteration_index += 1

        return [result, result_sum]
    except ValueError:
        return ["Данные не найдены"]
