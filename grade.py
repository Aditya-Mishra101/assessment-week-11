"""
Debugging Olympics -- self-check grader.

Runs against a running instance of the API and checks whether each of the
3 intentional bugs has been fixed. Does not look at source code, only at
API behavior, so it works unmodified against both the FastAPI and NestJS
versions of this challenge.

Usage:
    python grade.py [--base-url http://localhost:8000]
"""

import argparse
import sys

import requests


def login(base_url: str, username: str, password: str) -> str:
    resp = requests.post(
        f"{base_url}/auth/login", json={"username": username, "password": password}
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def check_sql_injection(base_url: str, token: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    baseline = requests.get(f"{base_url}/tickets", params={"search": ""}, headers=headers)
    if baseline.status_code >= 400:
        return False
    total_tickets = len(baseline.json())

    payload = "zzz-does-not-exist' OR '1'='1' -- "
    resp = requests.get(f"{base_url}/tickets", params={"search": payload}, headers=headers)
    if resp.status_code >= 500:
        return False
    try:
        results = resp.json()
    except ValueError:
        return False
    if not isinstance(results, list):
        return False
    # Vulnerable: the payload short-circuits the WHERE clause and returns
    # every ticket. Fixed: the payload is treated as a literal search term
    # that matches nothing.
    return len(results) == 0 and total_tickets > 0


def check_auth_bypass(base_url: str, trainee_token: str) -> bool:
    headers = {"Authorization": f"Bearer {trainee_token}"}
    resp = requests.put(
        f"{base_url}/tickets/1/status", json={"status": "closed"}, headers=headers
    )
    return resp.status_code in (401, 403)


def check_missing_validation(base_url: str, token: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{base_url}/tickets",
        json={"title": "", "description": "bad", "priority": 999},
        headers=headers,
    )
    return resp.status_code in (400, 422)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    print(f"Grading {args.base_url} ...\n")

    try:
        admin_token = login(args.base_url, "admin", "admin123")
        trainee_token = login(args.base_url, "trainee", "trainee123")
    except Exception as exc:  # noqa: BLE001
        print(f"Could not log in -- is the server running? ({exc})")
        return 1

    checks = [
        ("SQL injection fixed (parameterized query)", check_sql_injection(args.base_url, trainee_token)),
        ("Auth bypass fixed (admin-only status update)", check_auth_bypass(args.base_url, trainee_token)),
        ("Missing validation fixed (rejects bad ticket data)", check_missing_validation(args.base_url, admin_token)),
    ]

    score = 0
    for name, passed in checks:
        status = "PASS" if passed else "FAIL"
        if passed:
            score += 1
        print(f"[{status}] {name}")

    print(f"\nScore: {score}/3")
    return 0 if score == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
