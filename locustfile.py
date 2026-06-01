from locust import HttpUser, task, between

class BotUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8443"

    @task(7)
    def send_message(self):
        self.client.post("/webhook", json={"message": {"text": "Сәлем"}}, catch_response=True)

    @task(2)
    def send_voice(self):
        self.client.post("/webhook", json={"message": {"voice": {"file_id": "test"}}}, catch_response=True)

    @task(1)
    def send_image(self):
        self.client.post("/webhook", json={"message": {"photo": [{"file_id": "test"}]}}, catch_response=True)
