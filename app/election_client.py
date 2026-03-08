from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import List

PAGE_PATH = "/PRVoteChartResult2082.aspx"
DATA_PATH = "/Handlers/SecureJson.ashx?file=JSONFiles/Election2082/Common/PRHoRPartyTop5.txt"
BASE_URLS = [
    "https://result.election.gov.np",
    "http://result.election.gov.np",
]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class PartyVote:
    party: str
    votes: int


def fetch_pr_votes(timeout_seconds: int = 30) -> List[PartyVote]:
    last_error: Exception | None = None
    for base_url in BASE_URLS:
        try:
            return _fetch_pr_votes_from_base(base_url, timeout_seconds=timeout_seconds)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(
        "Could not fetch PR vote data from Election Commission Nepal."
    ) from last_error


def _fetch_pr_votes_from_base(base_url: str, timeout_seconds: int) -> List[PartyVote]:
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(cookie_jar),
    )
    opener.addheaders = [("User-Agent", USER_AGENT)]

    page_url = urllib.parse.urljoin(base_url, PAGE_PATH)
    with opener.open(page_url, timeout=timeout_seconds) as resp:
        resp.read()

    csrf_token = _extract_csrf(cookie_jar)
    data_url = urllib.parse.urljoin(base_url, DATA_PATH)
    request = urllib.request.Request(
        data_url,
        headers={
            "X-CSRF-Token": csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": page_url,
            "Origin": base_url,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": USER_AGENT,
        },
    )

    with opener.open(request, timeout=timeout_seconds) as resp:
        payload = json.loads(resp.read().decode("utf-8-sig"))

    results: List[PartyVote] = []
    for item in payload:
        name = str(item.get("PoliticalPartyName", "")).strip()
        votes = int(float(item.get("TotalVoteReceived", 0) or 0))
        if name and votes > 0:
            results.append(PartyVote(name, votes))

    if not results:
        raise RuntimeError(f"No party vote data found at {data_url}")
    return results


def _extract_csrf(cookie_jar: CookieJar) -> str:
    for cookie in cookie_jar:
        if cookie.name == "CsrfToken":
            return cookie.value
    raise RuntimeError("CsrfToken cookie not found")

