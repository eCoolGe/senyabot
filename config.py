# Доверенные id пользователей telegram
TRUSTED_ID = [572564221]

# Буква начала считывания сумм, буква конца считывания сумм, число строки на которой находятся фамилии преподавателей
PAY_RANGES = ["C", "Z", "2"]
# (A2:Z2) Диапазон ячеек таблицы откуда считывать фамилии преподавателей
SURNAME_RANGES = f"A{PAY_RANGES[2]}:{PAY_RANGES[1]}{PAY_RANGES[2]}"
# Диапазон ячеек таблицы откуда считывать даты
DATE_RANGES = "B1:B10000"
# Диапазон ячеек лог таблицы, буква начала записи, буква конца записи
LOG_RANGES = ["B1:B10000", "B", "G"]
# Название лог листа
LOG_LISTNAME = "Лог"
# Название листа прихода
INCOME_LISTNAME = "Приход"
# Название листа зарплаты
SALARY_LISTNAME = "Зарплата"