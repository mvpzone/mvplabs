#!/usr/bin/env bash
# Ten requests through the door. Four of them carry no body.
set -u
U=${U:-http://localhost:10000}
req() { printf '%-6s %-14s -> ' "$1" "$2"; shift 2; curl -s -o /dev/null -w '%{http_code}\n' "$@"; }
req GET    /              "$U/"
req GET    /orders        "$U/orders"
req HEAD   /orders        -I "$U/orders"
req POST   /orders        "$U/orders" -d '{"item": 1}'
req POST   "/orders (empty)" -X POST "$U/orders" -H 'content-length: 0'
req DELETE /orders/7      -X DELETE "$U/orders/7"
req GET    /admin         "$U/admin"
req POST   /admin         "$U/admin" -d '{"grant": "everyone"}'
req POST   /orders        "$U/orders" -d '{"item": 2}'
req GET    /admin/users   "$U/admin/users"
