from locust import HttpUser, between, task


class CRMindUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health(self):
        self.client.get("/api/v1/health")
