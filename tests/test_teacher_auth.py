import json
import tempfile
import unittest
from http.cookies import SimpleCookie
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.responses import Response
from starlette.requests import Request

from src.app import (
    SESSION_COOKIE_NAME,
    TeacherLogin,
    authenticate_teacher,
    get_teacher_session,
    hash_teacher_password,
    login_teacher,
    logout_teacher,
    require_teacher,
    verify_teacher_password,
)


class TeacherAuthTests(unittest.TestCase):
    @staticmethod
    def request_with_cookie(token=None):
        headers = []
        if token is not None:
            headers.append((b"cookie", f"{SESSION_COOKIE_NAME}={token}".encode()))
        return Request(
            {
                "type": "http",
                "asgi": {"version": "3.0", "spec_version": "2.3"},
                "http_version": "1.1",
                "method": "POST",
                "scheme": "http",
                "path": "/auth/login",
                "raw_path": b"/auth/login",
                "query_string": b"",
                "headers": headers,
                "server": ("testserver", 80),
                "client": ("testclient", 50000),
                "root_path": "",
            }
        )

    def test_password_hash_verifies_only_matching_password(self):
        password_hash = hash_teacher_password("a-strong-test-password")

        self.assertTrue(verify_teacher_password("a-strong-test-password", password_hash))
        self.assertFalse(verify_teacher_password("incorrect-password", password_hash))

    def test_password_hash_rejects_short_passwords(self):
        with self.assertRaises(ValueError):
            hash_teacher_password("short")

    def test_authenticates_from_json_file_case_insensitively(self):
        password = "a-strong-test-password"
        credentials = {
            "teachers": [
                {"username": "staff@example.edu", "password_hash": hash_teacher_password(password)}
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            credentials_path = Path(directory) / "teachers.json"
            credentials_path.write_text(json.dumps(credentials), encoding="utf-8")
            with patch("src.app.TEACHER_CREDENTIALS_PATH", credentials_path):
                self.assertEqual(
                    authenticate_teacher("STAFF@example.edu", password),
                    "staff@example.edu",
                )
                self.assertIsNone(
                    authenticate_teacher("staff@example.edu", "wrong-password")
                )

    def test_login_sets_session_and_logout_invalidates_it(self):
        password = "a-strong-test-password"
        credentials = {
            "teachers": [
                {"username": "staff@example.edu", "password_hash": hash_teacher_password(password)}
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            credentials_path = Path(directory) / "teachers.json"
            credentials_path.write_text(json.dumps(credentials), encoding="utf-8")
            with patch("src.app.TEACHER_CREDENTIALS_PATH", credentials_path):
                response = Response()
                login_teacher(
                    TeacherLogin(username="staff@example.edu", password=password),
                    self.request_with_cookie(),
                    response,
                )

                cookie = SimpleCookie(response.headers["set-cookie"])
                token = cookie[SESSION_COOKIE_NAME].value
                self.assertEqual(
                    get_teacher_session(self.request_with_cookie(token)),
                    "staff@example.edu",
                )
                self.assertEqual(
                    require_teacher(self.request_with_cookie(token)),
                    "staff@example.edu",
                )

                logout_teacher(self.request_with_cookie(token), Response())
                with self.assertRaises(HTTPException) as error:
                    require_teacher(self.request_with_cookie(token))
                self.assertEqual(error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()