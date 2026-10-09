def place_order(client, sku: str, qty: int) -> str:
    order = client.create_order(sku=sku, qty=qty)
    return order["id"]
