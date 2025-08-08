# Мультибіржовий арбітражний бот v3.0m

**Автоматичний Telegram-бот для моніторингу арбітражу між spot та futures/margin для топових бірж: Binance, Bybit, Kucoin, Gateio, OKX, BingX, HTX, MEXC.**

---

## Основний функціонал

- **Пошук арбітражу** між спотом, ф’ючерсами та маржею для ТОП-5 монет на кожній увімкненій біржі.
- **Перевіряються лише ті символи, які реально є і на споті, і на ф’ючерсах.**
- **Асинхронна обробка:** миттєва перевірка багатьох монет/бірж.
- **Гнучке підключення бірж** (налаштовується у config.yaml).
- **Автоматичне кешування ф’ючерсних символів** (оновлення раз на 60 хвилин).
- **RotatingFileHandler:** лог-файл ніколи не переповнює диск.
- **Сповіщення в Telegram:** гарно оформлені, з емодзі, статусами і звуками.

---

## Встановлення

1. **Клонуй репозиторій**
    ```
    git clone https://github.com/VadymTeterin/bybit-arbitrage-bot.git
    cd bybit-arbitrage-bot
    ```

2. **Встанови залежності**
    ```
    pip install -r requirements.txt
    ```

3. **Створи та налаштуй config.yaml**
    - Додай API-ключі для кожної біржі, яку хочеш використовувати
    - Вкажи свій Telegram Bot Token і Chat ID

4. **Запусти бота**
    ```
    python main.py
    ```

---

## Швидкий старт для Telegram

1. Створи Telegram-бота через BotFather, отримай токен.
2. Додай токен та chat_id в config.yaml:
    ```yaml
    telegram:
      bot_token: "ТВОЙ_ТОКЕН"
      chat_id: "ТВОЙ_CHAT_ID"
    ```

---

## Приклад налаштувань для бірж

```yaml
exchanges:
  binance:
    enabled: true
    api_key: "BINANCE_API_KEY"
    api_secret: "BINANCE_SECRET"
    request_interval: 3
    min_volume: 100000
  bybit:
    enabled: true
    api_key: "BYBIT_API_KEY"
    api_secret: "BYBIT_SECRET"
    request_interval: 3
    min_volume: 100000
  # Додавай інші біржі за аналогією
