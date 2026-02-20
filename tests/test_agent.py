from src.main import app


def test_app_exists():
    assert app.title == "Nexus Agent"
