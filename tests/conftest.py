import os
import tempfile
from pathlib import Path

import pytest
from backend.factory import create_app
from backend.services.database import DATABASE_PATH, init_db


@pytest.fixture(scope="session")
def app():
    os.environ["FLASK_ENV"] = "testing"
    app = create_app(load_artifacts=False)
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="function")
def client(app):
    test_db_fd, test_db_path = tempfile.mkstemp(prefix="test_users_", suffix=".db")
    os.close(test_db_fd)
    test_db_path = Path(test_db_path)

    original_path = DATABASE_PATH
    try:
        from backend.services import database as db_module
        db_module.DATABASE_PATH = test_db_path
        init_db()
        with app.test_client() as client:
            yield client
    finally:
        try:
            os.remove(test_db_path)
        except OSError:
            pass
        db_module.DATABASE_PATH = original_path
