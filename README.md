# fastApiProject
FastApi project 
# MyFastApiProject

Проект на FastAPI с использованием PostgreSQL в качестве БД. Реализация REST API по работе с меню ресторана. Для более удобного запуска используется docker-compose. Версия 3. Добавлено кеширование с помощью редис, работа с базой данных вынесена в слой repositories. Работа с чтением и инвалидацией кеша вынесена в services, создан модуль RedisService, для работы с контейнером redis, к которому обращается каждый класс сервисов. Добавлены pre-commit хуки: black, flake8, mypy и другие. 
## Установка и запуск

Следуйте инструкциям ниже, чтобы установить и запустить проект на своем компьютере или сервере.

### Предварительные требования

Наличие:

- Docker
- Docker Compose

### Клонирование репозитория

```bash
git clone https://github.com/Ilya2520/MyFastAPIproject2.git
cd MyFastAPIproject2
```

### Запуск проекта

- В Pycharm открыть File -> settings -> python interpreter, добавить New enviroment
- Перейти в коммандной строке Windows в директорию проекта и запустить команду:
  ```
  venv\Scripts\activate
  ```
- Далее выполнить следующую команду(docker должен быть установлен и запущен с правами администратора)
```
docker-compose up --build
```
- Теперь программа готова к тестированию

### Запуск тестирования
Если виртуальное окружение не было запущено, то:

- В Pycharm открыть File -> settings -> python interpreter, добавить New enviroment
- Перейти в коммандной строке Windows в директорию проекта и запустить команду:
  ```
  venv\Scripts\activate
  ```
Для запуска тестов запустите следующую команду
```
docker-compose -f docker-compose-test.yml up
```
### Структура проекта

- app/ - директория с файлами приложения
- docker/ - директория с Docker-контейнерами и Docker-файлами
- requirements.txt - файл зависимостей для установки необходимых пакетов
