import random
import time
import math
from typing import Iterator
from concurrent.futures import ThreadPoolExecutor


def gen_data(n: int = 75_000) -> Iterator[dict]:
    for i in range(75_000):
        user = {
            "id": i,
            "age": random.randint(18, 80),
            "score": random.randint(1, 10000),
            "email": f"user{i}@example.com",
        }
        yield user


def is_prime(n: int) -> bool:
    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    _is_prime = True
    for i in range(2, int(math.sqrt(n)) + 2):
        if n % i == 0:
            _is_prime = False
            break

    return _is_prime


def check_email(user) -> tuple[str, bool]:
    time.sleep(0.001)  # simulate I/O delay

    will_include = user["score"] % 3 == 0 and user["email"].startswith("user1")

    return user["email"], will_include


def get_score(user: dict) -> float:
    time.sleep(0.001)  # simulate model latency

    name = user["email"].split("@")[0]  # pretend we're doing name-based scoring
    name_entropy = sum(ord(c) ** 1.5 for c in name)  # unnecessary power ops
    behavior_factor = math.sin(user["score"] / 17) + math.log1p(user["age"])
    noise = sum([random.random() * 0.1 for _ in range(100)])  # artificial noise

    score = name_entropy * behavior_factor + noise

    return score


if __name__ == "__main__":
    start = time.time()

    """
        Ideas for optimization
          - [ ] List comprehension
          - 
    """

    prime_users = (user for user in gen_data(75_000) if is_prime(user["id"]))

    # print(f"Total number of prime users {len(prime_users)}")

    # Complex and inefficient scoring logic
    """
        Ideas to optimize 
          - [ ]
    
    """
    total_score = 0
    with ThreadPoolExecutor(max_workers=100) as pool:
        for score in pool.map(get_score, prime_users):
            total_score += int(score)

    # Artificially slow sort and filter
    """
        Ideas to optimize 
          - [ ]
    
    """

    sorted_users = sorted(prime_users, key=lambda u: u["score"], reverse=True)

    with ThreadPoolExecutor(max_workers=100) as pool:
        sorted_emails = [
            email
            for email, condition in pool.map(check_email, sorted_users)
            if condition
        ]

    end = time.time()

    print(f"Total score from prime users: {total_score}")
    print(f"Filtered emails: {sorted_emails[:10]} ...")
    print(f"Execution time: {end - start:.2f} seconds")
