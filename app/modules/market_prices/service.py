"""Resolve human-readable filters and normalize CEDA Agmarknet prices."""

from copy import deepcopy
from datetime import date, timedelta
from typing import Any

import httpx


SOURCE = "CEDA Agri Market Data (Agmarknet)"
ATTRIBUTION = "Centre for Economic Data & Analysis, Ashoka University"
PRICE_UNIT = "INR_PER_QUINTAL"


class MarketPriceError(Exception):
    """Base error safe to translate into an API response."""


class MarketPriceLookupError(MarketPriceError):
    """A requested commodity or geography was not found."""


class MarketPriceUpstreamError(MarketPriceError):
    """CEDA was unavailable or returned an invalid payload."""


_response_cache: dict[tuple, dict[str, Any]] = {}


def _items(payload: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), list):
        raise MarketPriceUpstreamError("CEDA returned an unexpected response")
    if not all(isinstance(item, dict) for item in payload[key]):
        raise MarketPriceUpstreamError("CEDA returned an unexpected response")
    return payload[key]


def _match(items: list[dict[str, Any]], name_key: str, value: str) -> dict[str, Any] | None:
    wanted = value.strip().casefold()
    return next((item for item in items if str(item.get(name_key, "")).strip().casefold() == wanted), None)


def _json(client: httpx.Client, method: str, path: str, **kwargs) -> Any:
    try:
        response = client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        raise MarketPriceUpstreamError("CEDA market prices are temporarily unavailable") from exc


def fetch_market_prices(
    *,
    api_key: str,
    base_url: str,
    commodity: str,
    state: str,
    district: str,
    market: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> dict[str, Any]:
    """Fetch lookup data and normalize the documented CEDA price response."""
    end = to_date or date.today()
    start = from_date or end - timedelta(days=30)
    cache_key = (commodity.casefold(), state.casefold(), district.casefold(), (market or "").casefold(), start, end)

    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    # A trailing slash plus relative paths preserves CEDA's documented ``/v1``
    # prefix. Leading-slash request paths would otherwise reset to the host root.
    with httpx.Client(base_url=f"{base_url.rstrip('/')}/", headers=headers, timeout=12.0) as client:
        commodities = _items(_json(client, "GET", "agmarknet/commodities"), "commodities")
        commodity_item = _match(commodities, "name", commodity)
        if commodity_item is None or "id" not in commodity_item:
            raise MarketPriceLookupError(f"Commodity {commodity!r} was not found by CEDA")

        geographies = _items(_json(client, "GET", "agmarknet/geographies"), "geographies")
        state_item = _match(geographies, "state_name", state)
        if state_item is None or "state_id" not in state_item:
            raise MarketPriceLookupError(f"State {state!r} was not found by CEDA")
        districts = state_item.get("districts")
        if not isinstance(districts, list):
            raise MarketPriceUpstreamError("CEDA returned an unexpected geography response")
        district_item = _match(districts, "district_name", district)
        if district_item is None or "district_id" not in district_item:
            raise MarketPriceLookupError(f"District {district!r} was not found in {state_item['state_name']}")

        market_payload = {
            "commodity_id": commodity_item["id"],
            "state_id": state_item["state_id"],
            "district_id": district_item["district_id"],
            "indicator": "price",
        }
        market_items = _items(_json(client, "POST", "agmarknet/markets", json=market_payload), "data")
        if market:
            selected = _match(market_items, "market_name", market)
            if selected is None:
                raise MarketPriceLookupError(f"Market {market!r} was not found in {district_item['district_name']}")
            market_items = [selected]
        if not market_items or any("market_id" not in item for item in market_items):
            raise MarketPriceLookupError("No CEDA markets were found for these filters")

        market_names = {item["market_id"]: item.get("market_name") or f"Market {item['market_id']}" for item in market_items}
        prices_payload = {
            "commodity_id": commodity_item["id"],
            "state_id": state_item["state_id"],
            "district_id": [district_item["district_id"]],
            "market_id": list(market_names),
            "from_date": start.isoformat(),
            "to_date": end.isoformat(),
        }
        records = _items(_json(client, "POST", "agmarknet/prices", json=prices_payload), "data")

    normalized = []
    required = {"date", "market_id", "min_price", "max_price", "modal_price"}
    for record in records:
        if not required.issubset(record):
            raise MarketPriceUpstreamError("CEDA returned an unexpected price response")
        try:
            observation = date.fromisoformat(str(record["date"])[:10])
            normalized.append({
                "market": market_names.get(record["market_id"], f"Market {record['market_id']}"),
                "market_id": int(record["market_id"]),
                "date": observation.isoformat(),
                "min_price": float(record["min_price"]),
                "max_price": float(record["max_price"]),
                "modal_price": float(record["modal_price"]),
            })
        except (TypeError, ValueError) as exc:
            raise MarketPriceUpstreamError("CEDA returned an unexpected price response") from exc

    normalized.sort(key=lambda item: item["date"], reverse=True)
    latest = date.fromisoformat(normalized[0]["date"]) if normalized else None
    result = {
        "source": SOURCE,
        "attribution": ATTRIBUTION,
        "price_unit": PRICE_UNIT,
        "commodity": str(commodity_item["name"]),
        "state": str(state_item["state_name"]),
        "district": str(district_item["district_name"]),
        "latest_observation": latest.isoformat() if latest else None,
        "age_days": max((date.today() - latest).days, 0) if latest else None,
        "stale_cache": False,
        "markets": normalized,
    }
    _response_cache[cache_key] = deepcopy(result)
    return result


def cached_market_prices(**filters) -> dict[str, Any] | None:
    key = (
        filters["commodity"].casefold(), filters["state"].casefold(), filters["district"].casefold(),
        (filters.get("market") or "").casefold(), filters["from_date"], filters["to_date"],
    )
    cached = _response_cache.get(key)
    if cached:
        result = deepcopy(cached)
        result["stale_cache"] = True
        return result
    return None
