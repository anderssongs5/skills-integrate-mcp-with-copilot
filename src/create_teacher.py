import json
import os
import secrets
from getpass import getpass
from pathlib import Path

from app import hash_teacher_password


CREDENTIALS_PATH = Path(__file__).with_name("teachers.json")


def main():
    username = input("Teacher username: ").strip()
    if not username:
        raise SystemExit("Username cannot be blank.")

    password = getpass("Teacher password (at least 12 characters): ")
    confirmation = getpass("Confirm password: ")
    if not secrets.compare_digest(password, confirmation):
        raise SystemExit("Passwords do not match.")

    try:
        password_hash = hash_teacher_password(password)
    except ValueError as error:
        raise SystemExit(str(error))

    if CREDENTIALS_PATH.exists():
        with CREDENTIALS_PATH.open(encoding="utf-8") as credentials_file:
            credentials = json.load(credentials_file)
    else:
        credentials = {"teachers": []}

    teachers = credentials.get("teachers")
    if not isinstance(teachers, list):
        raise SystemExit("teachers.json must contain a teachers list.")

    teacher = next(
        (
            item for item in teachers
            if isinstance(item, dict)
            and isinstance(item.get("username"), str)
            and item["username"].casefold() == username.casefold()
        ),
        None,
    )
    if teacher is None:
        teachers.append({"username": username, "password_hash": password_hash})
    else:
        teacher["password_hash"] = password_hash

    temporary_path = CREDENTIALS_PATH.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(credentials, indent=2) + "\n", encoding="utf-8"
    )
    os.chmod(temporary_path, 0o600)
    temporary_path.replace(CREDENTIALS_PATH)
    print(f"Teacher credentials saved to {CREDENTIALS_PATH}.")


if __name__ == "__main__":
    main()