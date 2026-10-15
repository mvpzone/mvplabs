from timekeeper.tools import lookup_timezone


def test_known_city_any_case():
    assert lookup_timezone(" Tokyo ") == {"status": "success", "city": " Tokyo ", "timezone": "Asia/Tokyo"}


def test_unknown_city_is_an_error_not_a_guess():
    result = lookup_timezone("Atlantis")
    assert result["status"] == "error"
    assert "Atlantis" in result["error_message"]


def test_paris():
    assert lookup_timezone("Paris")["timezone"] == "Europe/Paris"
