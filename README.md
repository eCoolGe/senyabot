# SenyaBot

### Описание
описание

___

### Запуск программы

`pip install -r requirements.txt`

`python` _(проверялось на версии 3.10.7)_

`cp .env.example .env`

`python spreadsheets_create.py` _(запускается один раз для создания ботом таблицы)_

`python bot.py`

___

### Вспомогательные материалы

1. _Генерация красивой Google-таблицы в [этой статье](https://habr.com/ru/post/305378/)_
2. _В [этой статье](https://habr.com/ru/post/483302/) четко описано, как настроить сервисный аккаунт для взаимодействия с Google Spreadsheets и не только_
3. _"Книга" для понимания взаимодействия python и библиотеки aiogram 2.0 находится по [этой ссылке](https://mastergroosha.github.io/aiogram-2-guide/)_
4. _Новый взгляд автора предыдущей ссылки на обновленную версию библиотеки aiogram 3.0 находится по [этой ссылке](https://mastergroosha.github.io/aiogram-3-guide/)_
5. _Еще один гайд по библиотеке aiogram по [этой ссылке](https://surik00.gitbooks.io/aiogram-lessons/content/)_
6. _А [эта ссылка](https://docs.aiogram.dev/ru/latest/index.html) на официальный GitHub вышеупомянутой библиотеки_

___

### Разворачиваем на хостинге

_Для выполнения задачи был выбран [этот хостинг](https://cp.beget.com/), а процесс полного разворачивания можно изучить в [видео](https://www.youtube.com/watch?v=ibwjI6mKwLM)_

<details>
<summary>Подробности разворачивания на хостинге</summary>

_Для того чтобы бот сам запускался после перезапуска сервера или при падении скрипта, необходимо:_

* Создать скрипт его запуска одной из папок (на сколько я понял, в зависимости от версии Ubuntu)
  * `/usr/lib/systemd/system`
  * `/etc/init.d`
```
#!/bin/bash
### BEGIN INIT INFO
# Provides:          haltusbpower
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Halts USB power...
### END INIT INFO

[Unit]
Description=SenyaBot
After=syslog.target
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/SenyaBot
ExecStart=nohup python3 /home/SenyaBot/bot.py &
RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
```

* `sudo systemctl daemon-reload` — Перезагружаем список всех служб после каждого редактирования этого файла
* `sudo systemctl enable senyabot.service` — включаем службу, чтобы не отключалась при перезапуске
* Так же у нас есть другой список доступных команд:
  * `sudo systemctl start senyabot.service` — запустить службу
  * `sudo systemctl stop senyabot.service` — остановить службу
  * `sudo systemctl status senyabot.service` — посмотреть статус, работает или нет
* Подробности можно найти в [этой статье](https://thecode.media/systemctl/)

</details>