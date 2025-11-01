# Образовательная платформа

Django REST API для управления курсами и уроками с системой подписок и уведомлений.

## 🐳 Запуск через Docker Compose

### Предварительные требования
- Docker
- Docker Compose

### Быстрый старт

1. **Клонируйте репозиторий**
   ```
   git clone <your-repo-url>
   cd Python_Homework_4
   ```
Настройте переменные окружения

cp .env.example .env
Отредактируйте файл .env и установите ваши значения:

SECRET_KEY - сгенерируйте случайный ключ для Django

Настройте базу данных, email, Stripe ключи

Запустите проект

bash
docker-compose up -d --build
Примените миграции (выполняются автоматически)

bash
docker-compose exec backend python manage.py migrate
Создайте суперпользователя

bash
docker-compose exec backend python manage.py createsuperuser
Приложение доступно по адресу

Главная: http://localhost:8000/

Админка: http://localhost:8000/admin

Документация API: http://localhost:8000/swagger/

🔧 Проверка работоспособности сервисов
1. Бэкенд (Django)
bash
# Проверить статус
```
docker-compose ps backend
```

# Просмотреть логи
```
docker-compose logs backend
```
# Проверить доступность
curl http://localhost:8000/api/courses/
2. База данных (PostgreSQL)
# Проверить подключение
```
docker-compose exec db pg_isready
```
# Проверить базу данных
```
docker-compose exec db psql -U postgres -d homework_4 -c "\dt"
```
3. Redis
# Проверить работу
```
docker-compose exec redis redis-cli ping
```
# Проверить подключение из приложения
```
docker-compose exec backend python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
```
4. Celery Worker
# Проверить статус
```
docker-compose ps celery
```
# Просмотреть логи
```
docker-compose logs celery
```
5. Celery Beat
# Проверить статус
```
docker-compose ps celery_beat
```
# Просмотреть логи
```
docker-compose logs celery_beat
```
📊 Проверка функциональности
API endpoints

Курсы: http://localhost:8000/api/courses/

Уроки: http://localhost:8000/api/lessons/

Подписки: POST http://localhost:8000/api/subscription/

Админ панель

Войдите в http://localhost:8000/admin

Управляйте курсами, уроками, пользователями

Периодические задачи

Ежедневный дайджест в 9:00

Уведомления об обновлениях курсов

🛠 Полезные команды
bash
# Остановить все сервисы
```
docker-compose down
```
# Перезапустить конкретный сервис
```
docker-compose restart backend
```
# Просмотреть логи всех сервисов
```
docker-compose logs -f
```
# Выполнить команду в контейнере
```
docker-compose exec backend python manage.py shell
```
# Очистка системы
docker system prune
📁 Структура сервисов
* backend -	8000 -	Django приложение
* db -	5432 -	PostgreSQL база данных
* redis -	6379 -	Redis кэш и брокер
* celery	-	Celery worker - для фоновых задач
* celery_beat	-	Celery beat - для периодических задач

🔐 Безопасность
Все чувствительные данные вынесены в .env

Файл .env добавлен в .gitignore

Используется .env.example как шаблон
