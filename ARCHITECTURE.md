# Архитектура SISU Bot

```mermaid
graph TD
    subgraph Telegram
        User["Пользователь (Telegram)"]
    end
    subgraph Bot
        BotCore["SISU Bot (aiogram)"]
        Handlers["Handlers (команды, медиа, игры)"]
        Middlewares["Middlewares (антифрод, лимиты, sync)"]
        Services["Services (баллы, топы, донат, TTS)"]
        DB["SQLite/Postgres DB"]
        DataFiles["JSON-файлы (users, ranks, games)"]
        Logger["Логирование (bot.log)"]
    end
    subgraph AdminPanel
        AdminApp["FastAPI Admin Panel"]
        AdminUI["Web UI"]
    end
    subgraph Ext
        YandexTTS["Yandex SpeechKit TTS"]
        TON["TON Blockchain"]
    end

    User-->|"/команды, медиа"|BotCore
    BotCore-->|"Обработка"|Handlers
    BotCore-->|"Проверки"|Middlewares
    Handlers-->|"Бизнес-логика"|Services
    Services-->|"Чтение/запись"|DB
    Services-->|"Чтение/запись"|DataFiles
    Services-->|"TTS"|YandexTTS
    Services-->|"Донат"|TON
    BotCore-->|"Логи"|Logger
    AdminUI-->|"REST API"|AdminApp
    AdminApp-->|"Управление"|DB
    AdminApp-->|"Управление"|DataFiles
    AdminApp-->|"Мониторинг"|Logger
```

## Описание компонентов

- **SISU Bot (aiogram)** — основной Telegram-бот, обрабатывает команды, медиа, игры, начисляет баллы, следит за лимитами и антифродом.
- **Handlers** — обработчики команд, медиа, игровых сценариев.
- **Middlewares** — антифрод, лимиты, синхронизация пользователей, разрешённые чаты.
- **Services** — бизнес-логика: баллы, топы, донат, TTS, рефералы, игры.
- **DB** — основная база (SQLite или Postgres), хранит пользователей, баллы, транзакции, логи.
- **DataFiles** — json-файлы с дополнительными данными (users, ranks, games, фразы).
- **Logger** — логирование действий и ошибок (bot.log).
- **Admin Panel** — FastAPI-приложение для управления ботом, пользователями, логами, мониторингом.
- **Yandex SpeechKit** — внешний сервис для генерации TTS.
- **TON Blockchain** — интеграция для доната и NFT.

---

**Диаграмма отражает все ключевые связи между компонентами, внешними сервисами и пользователями.** 