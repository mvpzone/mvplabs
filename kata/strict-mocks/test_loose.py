from unittest.mock import MagicMock

from checkout import place_order


def test_place_order_returns_the_id():
    client = MagicMock()
    client.submit_order.return_value = {"id": "ord-1"}
    assert place_order(client, "sku-42", 1) == "ord-1"
