# Bybit Arbitrage Telegram Bot

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Bybit](https://img.shields.io/badge/Bybit-API-yellow)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)
![Async](https://img.shields.io/badge/Asyncio-Fast-green)

---

## Опис

**Bybit Arbitrage Telegram Bot** — асинхронний бот для моніторингу топ-5 монет з найбільшим арбітражем між спотом і ф’ючерсами на біржі Bybit.  
Бот автоматично враховує лише ліквідні монети (за фільтром обсягу) та надсилає алерти в Telegram.

---

## Можливості

- 🔥 Пошук топ-5 монет з найбільшим арбітражем
- 💧 Фільтрація монет за 24h обсягом (min_volume)
- 🕒 Кешування списку монет для швидкої роботи
- 🚫 Антиспам: сигнал надсилається лише при зміні топ-5
- 🛡️ Гарні старт/стоп повідомлення в Telegram
- 📈 Робота 24/7 — готовий до запуску на VPS/сервері
- 🗂️ Зручний лог роботи в bot.log

---

## Вимоги

- Python 3.10+
- Аккаунт на [Bybit](https://www.bybit.com/) та API ключ (тільки читання)
- Telegram-бот (токен через @BotFather) та chat_id

---

## Встановлення та запуск

1. **Клонуй репозиторій:**
   ```bash
   git clone <your-repo-link>
   cd bybit-arbitrage-bot
Встанови залежності:

bash
Копіювати
Редагувати
pip install pybit python-telegram-bot aiohttp pyyaml python-dotenv
Створи та заповни файл config.yaml:

yaml
Копіювати
Редагувати
bybit:
  api_key: "ТВОЙ_BYBIT_API_KEY"
  api_secret: "ТВОЙ_BYBIT_API_SECRET"
  arbitrage_difference: 1.0         # Поріг арбітражу, %
  request_interval: 3               # Інтервал запитів, сек
  min_volume: 100000                # Мінімальний обсяг торгів за 24h (USDT)
telegram:
  bot_token: "ТВОЙ_TELEGRAM_BOT_TOKEN"
  chat_id: "ТВОЙ_CHAT_ID"
Рекомендація: не додавати config.yaml у публічний репозиторій!

Запусти бота:

bash
Копіювати
Редагувати
python main.py
Як працює
Після запуску: Бот надсилає стартове повідомлення в Telegram.

Кожен цикл: Кешує список ліквідних монет (оновлює раз на 10 хвилин), перевіряє арбітраж між спотом і ф’ючерсами.

Якщо топ-5 змінився: Надсилає інформативний сигнал у Telegram.

Зупинка (Ctrl+C або помилка): Надсилає повідомлення про зупинку з часом і причиною.

Логування
Всі події та помилки пишуться у файл bot.log.

Для глибшого аналізу можна розширити логування або додати збереження сигналів у CSV/базу.

Розгортання 24/7 (рекомендовано VPS/сервер)
Через systemd (Ubuntu, Debian, CentOS):
Створи юніт-файл /etc/systemd/system/bybit-bot.service:

ini
Копіювати
Редагувати
[Unit]
Description=Bybit Arbitrage Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/home/yourusername/bybit-arbitrage-bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
Активуй:

bash
Копіювати
Редагувати
sudo systemctl daemon-reload
sudo systemctl enable bybit-bot
sudo systemctl start bybit-bot
Через tmux або screen:
bash
Копіювати
Редагувати
tmux
python main.py
# натисни Ctrl+B, потім D — сесія працює у фоні
Налаштування
arbitrage_difference — мінімальна різниця (у %) між ціною ф'ючерсу і споту для сигналу.

request_interval — затримка між перевірками в секундах.

min_volume — мінімальний добовий обсяг торгів для монети (USDT).

FAQ
1. Не надходять повідомлення в Telegram?
— Перевір правильність bot_token та chat_id, а також чи додав бота у свій чат.

2. Бот надто часто сигналить?
— Підвищ arbitrage_difference або min_volume у config.yaml.

3. Чи безпечно використовувати API-ключі?
— Для бота достатньо прав "Read-Only". Не давай доступ до торгівлі!

Ліцензія
MIT License.
Використовуй на свій страх і ризик.

Автор: VadymTeterin
З питаннями — у Telegram: @IIIpekk