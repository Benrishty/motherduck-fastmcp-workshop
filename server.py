"""Your MCP server for San Francisco 311 data.

FastMCP Gateway runs this file. Its entrypoint setting is `server.py:mcp`.
"""

from collections import Counter, defaultdict
from statistics import median
from typing import Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from sf311.data import BY_ID, LOCAL_NAMES, NEIGHBORHOODS, REQUESTS, SERVICES, Request, closest

mcp = FastMCP("sf-311")

MAX_ROWS = 50
MIN_CLOSED_FOR_MEDIAN = 10

GROUPS = {
    "neighborhood": lambda r: r.neighborhood,
    "service": lambda r: r.service,
    "agency": lambda r: r.agency,
    "source": lambda r: r.source,
    "weekday": lambda r: r.opened.strftime("%A"),
    "status": lambda r: r.status,
}

READ_ONLY = {"readOnlyHint": True}


def _check(value: str | None, choices: list[str], kind: str) -> None:
    if value is None or value in choices:
        return
    suggestions = closest(value, choices)
    hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
    raise ToolError(f"Unknown {kind} {value!r}.{hint} Call dataset_info for the exact {kind} names.")


def _matching(service: str | None = None, neighborhood: str | None = None, status: str | None = None) -> list[Request]:
    _check(service, SERVICES, "service")
    _check(neighborhood, NEIGHBORHOODS, "neighborhood")
    return [
        r
        for r in REQUESTS
        if (service is None or r.service == service)
        and (neighborhood is None or r.neighborhood == neighborhood)
        and (status is None or r.status == status)
    ]


COLUMNS_URI = "sf311://columns"

COLUMNS = {
    "request_id": {
        "csv_column": "service_request_id",
        "meaning": "The request's ID. Pass it to get_request.",
    },
    "opened": {
        "csv_column": "requested_datetime",
        "meaning": "When the request was opened, ISO 8601 in San Francisco local time.",
    },
    "closed": {
        "csv_column": "closed_date",
        "meaning": "When it was closed, ISO 8601 local time. null while the request is open.",
    },
    "status": {
        "csv_column": "status_description",
        "meaning": "Open or Closed.",
    },
    "service": {
        "csv_column": "service_name",
        "meaning": "What the request is about, such as Graffiti Public. Exact names come from dataset_info.",
    },
    "subtype": {
        "csv_column": "service_subtype",
        "meaning": "A finer category within the service.",
    },
    "agency": {
        "csv_column": "agency_responsible",
        "meaning": "The city team that owns the request.",
    },
    "neighborhood": {
        "csv_column": "analysis_neighborhood",
        "meaning": "One of the city's 41 official neighborhoods, or empty when unknown.",
    },
    "local_name": {
        "csv_column": "neighborhoods_sffind_boundaries",
        "meaning": "The name people use for the area, such as Lower Nob Hill. One name can span several official neighborhoods.",
    },
    "address": {
        "csv_column": "address",
        "meaning": "Where the problem is.",
    },
    "source": {
        "csv_column": "source",
        "meaning": "How it was filed: Mobile, Web, Phone, Integrated Agency, Twitter, or Email.",
    },
}


@mcp.resource(
    COLUMNS_URI,
    name="columns",
    description="What each field in a 311 request means, as returned by search_requests and get_request.",
    mime_type="application/json",
)
def columns() -> dict:
    """Describe every field of a 311 request and the CSV column it comes from."""
    return {
        "fields": COLUMNS,
        "notes": [
            "Each row is one report a resident filed with the city during one week in October 2026.",
            "count_requests can group by neighborhood, service, agency, source, weekday (of opened), or status.",
            "median_close_hours uses only closed requests: hours from opened to closed.",
        ],
    }


@mcp.tool(annotations=READ_ONLY)
def dataset_info() -> dict:
    """Describe the 311 dataset this server answers questions about.

    Call this first to learn the date range and the exact service and
    neighborhood names that other tools accept. For what each field of a
    request means, read the resource named in columns_resource.
    """
    return {
        "description": "San Francisco 311 service requests filed in one week.",
        "first_opened": min(request.opened for request in REQUESTS).isoformat(),
        "last_opened": max(request.opened for request in REQUESTS).isoformat(),
        "requests": len(REQUESTS),
        "services": SERVICES,
        "neighborhoods": NEIGHBORHOODS,
        "local_neighborhood_names": len(LOCAL_NAMES),
        "columns_resource": COLUMNS_URI,
    }


@mcp.tool(annotations=READ_ONLY)
def count_requests(
    service: str | None = None,
    neighborhood: str | None = None,
    group_by: Literal["neighborhood", "service", "agency", "source", "weekday", "status"] | None = None,
) -> int | dict[str, int]:
    """Count this week's 311 requests, optionally filtered and broken down.

    Use this for any "how many", "which has the most", or ranking question.
    Without group_by it returns one number. With group_by it returns a dict of
    group -> count, largest first (ties alphabetical), at most 50 groups, so
    the first key is the top group. Requests with no value for the grouping
    field are left out of the breakdown.

    Example: the neighborhood with the most Encampment requests is the first
    key of count_requests(service="Encampment", group_by="neighborhood").

    service and neighborhood must be exact names from dataset_info.
    For individual requests use search_requests; for closing times use
    median_close_hours.
    """
    rows = _matching(service, neighborhood)
    if group_by is None:
        return len(rows)
    key = GROUPS[group_by]
    counts = Counter(key(r) for r in rows if key(r))
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return dict(ranked[:MAX_ROWS])


@mcp.tool(annotations=READ_ONLY)
def median_close_hours(
    service: str | None = None,
    group_by: Literal["neighborhood", "agency"] | None = None,
) -> float | None | dict[str, float]:
    """Median hours from opened to closed for this week's closed 311 requests.

    Use this for "how fast" questions. Only closed requests count; open ones
    are ignored. Without group_by it returns one number of hours (rounded to
    0.1), or null if nothing matching has closed. With group_by it returns a
    dict of group -> median hours, fastest first, leaving out groups with
    fewer than 10 closed requests.

    service must be an exact name from dataset_info. To count requests use
    count_requests instead.
    """
    rows = [r for r in _matching(service) if r.hours_to_close is not None]
    if group_by is None:
        return round(median(r.hours_to_close for r in rows), 1) if rows else None
    key = GROUPS[group_by]
    hours: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if key(r):
            hours[key(r)].append(r.hours_to_close)
    medians = {g: round(median(v), 1) for g, v in hours.items() if len(v) >= MIN_CLOSED_FOR_MEDIAN}
    return dict(sorted(medians.items(), key=lambda item: (item[1], item[0]))[:MAX_ROWS])


@mcp.tool(annotations=READ_ONLY)
def search_requests(
    service: str | None = None,
    neighborhood: str | None = None,
    status: Literal["Open", "Closed"] | None = None,
    limit: int = 20,
) -> list[dict]:
    """List individual 311 requests, newest first.

    Use this to see examples: addresses, subtypes, timestamps, request ids.
    Returns at most `limit` rows (1 to 50), so never use it to count or rank;
    use count_requests for that. service and neighborhood must be exact names
    from dataset_info. Pass a returned request_id to get_request for one
    request on its own.
    """
    if not 1 <= limit <= MAX_ROWS:
        raise ToolError(f"limit must be between 1 and {MAX_ROWS}. To count requests, use count_requests instead.")
    rows = sorted(_matching(service, neighborhood, status), key=lambda r: r.opened, reverse=True)
    return [r.as_dict() for r in rows[:limit]]


@mcp.tool(annotations=READ_ONLY)
def get_request(request_id: str) -> dict:
    """Get one 311 request by its request_id, with every field.

    Use this when you already have an id, for example from search_requests.
    To find requests by service or neighborhood, use search_requests.
    """
    request = BY_ID.get(request_id.strip())
    if request is None:
        raise ToolError(f"No request with id {request_id!r}. Use search_requests to find request ids.")
    return request.as_dict()


if __name__ == "__main__":
    mcp.run()
