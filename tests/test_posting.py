import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms.simulated import FakeOne, FakeThree, FakeTwo
from app.services import posting_service

client = TestClient(app)
GOOD = "Check out our platform. https://example.com"


@pytest.fixture(autouse=True)
def use_fake_platforms(monkeypatch):
    monkeypatch.setattr(
        posting_service, "PLATFORMS", [FakeOne(), FakeTwo(), FakeThree()]
    )

    async def fake_public(url):
        return True

    monkeypatch.setattr(posting_service, "_is_public", fake_public)


def post(message):
    return client.post("/posting", json={"message": message})


def test_valid_message_posts_to_all_platforms():
    r = post(GOOD)
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert len(r.json()["results"]) == 3


def test_one_failure_does_not_stop_others():
    results = post(GOOD).json()["results"]
    statuses = {x["platform"]: x["status"] for x in results}
    assert statuses == {
        "Fake One": "success",
        "Fake Two": "success",
        "Fake Three": "failed",
    }
    failed = next(x for x in results if x["status"] == "failed")
    assert failed["error"] == "Authentication failed"
    assert failed["posted_url"] is None


def test_result_has_required_fields():
    result = post(GOOD).json()["results"][0]
    assert set(result) == {
        "platform", "status", "posted_url", "public_access", "date", "time", "error",
    }


def test_all_platforms_failing_gives_success_false(monkeypatch):
    monkeypatch.setattr(posting_service, "PLATFORMS", [FakeThree()])
    assert post(GOOD).json()["success"] is False


def test_message_without_link_rejected():
    assert post("Hello, no link here").status_code == 422


def test_message_with_two_links_rejected():
    assert post("One https://a.com and two https://b.com").status_code == 422


def test_message_too_long_rejected():
    assert post("a" * 190 + " https://example.com").status_code == 422


def test_message_of_exactly_200_chars_accepted():
    assert post("a" * 180 + " https://example.com").status_code == 200


def test_empty_message_rejected():
    assert post("").status_code == 422


def test_broken_link_rejected():
    assert post("see https://").status_code == 422