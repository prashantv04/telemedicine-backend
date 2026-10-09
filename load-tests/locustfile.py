import random
import string
from locust import HttpUser, task, between, events


def get_headers():
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyODYxODNlNS05Y2NmLTQxOGMtYjc1MC1jM2Q4Zjk1MzBiYjkiLCJyb2xlIjoicGF0aWVudCIsImV4cCI6MTc5MTU3Mjc0M30.6U3iUnylpfl4wQ112s0bAzwkksNcsLeVTcYyprMIaa4",
        "Content-Type": "application/json"
    }


class TelemedicineUser(HttpUser):
    # Simulates the time a user spends reading the screen before clicking again
    wait_time = between(1, 3)

    @task(3)  # Weight: 3x more likely to just browse doctors
    def fetch_doctors(self):
        # Target: p95 < 200ms
        with self.client.get(
                "/consultations/search?page=1&limit=20",
                headers=get_headers(),
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Read failed: {response.status_code}")

    @task(1)  # Weight: 1x
    def book_consultation(self):
        # Target: p95 < 500ms
        payload = {
            "doctor_id": "fa0f5a9b-5fc2-47c3-8bc4-433573f581a2",
            "patient_id": "286183e5-9ccf-418c-b750-c3d8f9530bb9",
            "slot_id": "35d1c001-c678-4dd1-91ce-243ef313485c"
        }

        # Inject the Idempotency-Key exactly as your architecture demands
        headers = get_headers()
        headers["Idempotency-Key"] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        with self.client.post(
                "/bookings",
                json=payload,
                headers=headers,
                catch_response=True
        ) as response:
            # We expect 201 (Created) or 409 (Conflict due to row-level locking)
            if response.status_code in [201, 409]:
                response.success()
            else:
                response.failure(f"Write failed: {response.status_code}")


# ==============================================================
# 🎯 AUTOMATED METRICS ENFORCEMENT (PROVES YOUR README CLAIMS)
# ==============================================================
@events.quitting.add_listener
def assert_performance_metrics(environment, **kwargs):
    if environment.stats.total.fail_ratio > 0.0005:
        print(f"❌ FAIL: Failure rate is {environment.stats.total.fail_ratio * 100}%. (Target: < 0.05%)")
        environment.process_exit_code = 1

    # Loop through endpoints and check latencies
    for (method, name), stats in environment.stats.entries.items():
        p95 = stats.get_response_time_percentile(0.95)

        if method == "GET" and p95 > 200:
            print(f"❌ FAIL: Read latency p95 is {p95}ms. (Target: < 200ms)")
            environment.process_exit_code = 1

        elif method == "POST" and p95 > 500:
            print(f"❌ FAIL: Write latency p95 is {p95}ms. (Target: < 500ms)")
            environment.process_exit_code = 1

    if environment.process_exit_code == 0:
        print("✅ SUCCESS: All performance metrics passed constraints!")