### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```sh
git clone https://github.com/aleklandra/api_yamdb.git
```

```sh
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```sh
python3 -m venv env
```

```sh
source venv/bin/activate
```

```sh
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```sh
pip install -r requirements.txt
```

Выполнить миграции:

```sh
python3 manage.py migrate
```

Запустить проект:

```sh
python3 manage.py runserver
```
