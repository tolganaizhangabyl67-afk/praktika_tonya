from locust import HttpUser, task, between
import json
import random

MESSAGES = [
    "привет",
    "погода в Алматы",
    "кто такой Насем Талеб",
    "какой сегодня день",
    "расскажи анекдот",
    "статья 610 КоАП РК",
    "курс доллара сегодня",
    "что такое антихрупкость",
]

class BotUser(HttpUser):
    wait_time = between(1, 3)
    
    # Симулируем webhook запросы от Telegram
    @task(7)
    def send_text_message(self):
        """70% — обычные текстовые запросы"""
        user_id = random.randint(100000, 999999)
        message = random.choice(MESSAGES)
        
        payload = {
            "update_id": random.randint(1000000, 9999999),
            "message": {
                "message_id": random.randint(1, 9999),
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": f"User{user_id}",
                    "username": f"user{user_id}"
                },
                "chat": {
                    "id": user_id,
                    "type": "private"
                },
                "date": 1716000000,
                "text": message
            }
        }
        
        self.client.post(
            "/webhook",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="text_message"
        )

    @task(2)
    def send_command(self):
        """20% — команды"""
        user_id = random.randint(100000, 999999)
        commands = ["/start", "/reset", "/mystats"]
        command = random.choice(commands)
        
        payload = {
            "update_id": random.randint(1000000, 9999999),
            "message": {
                "message_id": random.randint(1, 9999),
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": f"User{user_id}",
                    "username": f"user{user_id}"
                },
                "chat": {
                    "id": user_id,
                    "type": "private"
                },
                "date": 1716000000,
                "text": command,
                "entities": [{"offset": 0, "length": len(command), "type": "bot_command"}]
            }
        }
        
        self.client.post(
            "/webhook",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="command"
        )

    @task(1)
    def send_search(self):
        """10% — поиск"""
        user_id = random.randint(100000, 999999)
        queries = ["/search погода Алматы", "/search курс доллара", "/search новости Казахстан"]
        query = random.choice(queries)
        
        payload = {
            "update_id": random.randint(1000000, 9999999),
            "message": {
                "message_id": random.randint(1, 9999),
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": f"User{user_id}",
                    "username": f"user{user_id}"
                },
                "chat": {
                    "id": user_id,
                    "type": "private"
                },
                "date": 1716000000,
                "text": query,
                "entities": [{"offset": 0, "length": len(query.split()[0]), "type": "bot_command"}]
            }
        }
        
        self.client.post(
            "/webhook",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="search"
        )
