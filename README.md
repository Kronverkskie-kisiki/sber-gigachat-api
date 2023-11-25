### Запуск:
- Клоним репу
- Создаем файл `.env` со следующим контентом:
    ```
    client_secret=
    auth_data=
    client_id=
    scope=GIGACHAT_API_PERS
    access_token=
    expires_at=
    access_token_internal=
    ```
- `docker-compose build`
- `docker-compose up`
- приложение развернется на `localhost:5000`
- чтобы проверить что все работает `http://localhost:5000/api/health_check` - ответит 
    ```
    {
      "authenticated": false,
      "status": "ok"
    }
    ```

