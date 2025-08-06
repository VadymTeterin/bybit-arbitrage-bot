# Bybit Multi-Exchange Arbitrage Bot v3.0m

## 🚀 Опис

Цей бот відстежує арбітражні можливості між спотовими, маржинальними та ф'ючерсними ринками на топових криптобіржах (Bybit, Binance, OKX, Kucoin, Gateio, BingX, MEXC, HTX).
Підтримує підключення одразу до кількох бірж із гнучким керуванням через один конфігураційний файл.

---

## 🔧 Функціонал

- ТОП-5 сигналів арбітражу для кожної біржі окремо (spot-futures, margin-futures)
- Поріг арбітражу та мінімальний добовий обсяг налаштовуються
- Кешування монет для швидкої роботи й зниження навантаження на API
- Антиспам: сигнали надсилаються тільки при реальних змінах у топах
- Спец-алерт та гучна нотифікація для різниці понад 2%
- Повідомлення формуються для Telegram із вказанням біржі та ліквідності
- Легко розширюється на нові біржі та ринки (розширена структура проекту)

---

## ⚙️ Встановлення

1. **Склонуй репозиторій**
    ```bash
    git clone https://github.com/yourusername/bybit-arbitrage-bot.git
    cd bybit-arbitrage-bot
    ```

2. **Встанови залежності**
    ```bash
    pip install -r requirements.txt
    ```

3. **Скопіюй шаблон конфігу і заповни свої ключі**
    ```bash
    cp config.example.yaml config.yaml
    ```
    - Додай свої API-ключі для бірж, токен Telegram-бота та chat_id.
    - Увімкни потрібні біржі (`enabled: true`), за потреби скоригуй інтервали запитів.

4. **Запусти бота**
    ```bash
    python main.py
    ```

---

## 📁 Структура проекту

bybit-arbitrage-bot/
├── arbitrage_blocks/ # Алгоритми для кожної біржі (spot-futures, margin-futures)
├── cache/ # Кешування монет і TTL
├── exchanges/ # API-клієнти для кожної біржі
├── formatters/ # Формування повідомлень (текст/HTML)
├── utils/ # Антиспам, статистика, допоміжні
├── main.py # Orchestrator
├── telegram_bot.py # Відправка сигналів у Telegram
├── logger.py # Логування
├── config.yaml # (секретний, не потрапляє у git)
├── config.example.yaml # Шаблон для нових користувачів
├── requirements.txt # Python-залежності
├── CHANGELOG.md # Журнал змін
├── README.md # Ця інструкція
├── .gitignore # Не відстежує приватні файли
└── bot.log # Логи роботи (автоматично)


---

## 📦 Формат конфігурації (`config.yaml`)

Дивись шаблон у [config.example.yaml](config.example.yaml):

```yaml
exchanges:
  bybit:
    api_key: "YOUR_BYBIT_API_KEY"
    api_secret: "YOUR_BYBIT_API_SECRET"
    min_volume: 100000
    enabled: true
    request_interval: 2
  # ...інші біржі
arbitrage_difference: 1.0
request_interval: 3
telegram:
  bot_token: "YOUR_TELEGRAM_BOT_TOKEN"
  chat_id: "YOUR_TELEGRAM_CHAT_ID"

❗ Безпека
НІКОЛИ не коміть файл config.yaml у репозиторій!

Завжди зберігайте свої API-ключі лише локально або на сервері.

Для репозиторію використовуйте тільки config.example.yaml

🧑‍💻 Розширення
Додавай нові біржі через exchanges/ та arbitrage_blocks/

Легко додавай нові формати повідомлень у formatters/ (наприклад, HTML, email, Slack)

Пиши свої менеджери статистики чи додаткові антиспам-фільтри у utils/

📣 Підтримка та ідеї
Якщо маєш питання — створи Issue на GitHub або пиши у Telegram.

Pull requests на нові біржі/фічі — вітаються!

🏁 Ліцензія
MIT License. Весь код відкритий для спільноти. Не забувай дбати про безпеку своїх ключів!