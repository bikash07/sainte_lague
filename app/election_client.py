from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import Any, Dict, List

BASE_URLS = [
    "https://result.election.gov.np",
    "http://result.election.gov.np",
]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
PR_PAGE_PATH = "/PRVoteChartResult2082.aspx"
FPTP_PAGE_PATH = "/FPTPWLChartResult2082.aspx"
PR_DATA_FILE = "JSONFiles/Election2082/Common/PRHoRPartyTop5.txt"
FPTP_DATA_FILE = "JSONFiles/Election2082/Common/HoRPartyTop5.txt"
SECURE_JSON_PATH = "/Handlers/SecureJson.ashx?file={file_path}"


@dataclass(frozen=True)
class PartyVote:
    party: str
    votes: int


@dataclass(frozen=True)
class FPTPPartyResult:
    party: str
    won: int
    leading: int
    total: int


def fetch_pr_votes(timeout_seconds: int = 30) -> List[PartyVote]:
    last_error: Exception | None = None
    for base_url in BASE_URLS:
        try:
            payload = _fetch_secure_json(
                base_url=base_url,
                page_path=PR_PAGE_PATH,
                file_path=PR_DATA_FILE,
                timeout_seconds=timeout_seconds,
            )
            return _parse_pr_votes(payload)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(
        "Could not fetch PR vote data from Election Commission Nepal."
    ) from last_error


def fetch_fptp_results(timeout_seconds: int = 30) -> List[FPTPPartyResult]:
    last_error: Exception | None = None
    for base_url in BASE_URLS:
        try:
            payload = _fetch_secure_json(
                base_url=base_url,
                page_path=FPTP_PAGE_PATH,
                file_path=FPTP_DATA_FILE,
                timeout_seconds=timeout_seconds,
            )
            return _parse_fptp_results(payload)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(
        "Could not fetch FPTP party results from Election Commission Nepal."
    ) from last_error


def _fetch_secure_json(
    base_url: str,
    page_path: str,
    file_path: str,
    timeout_seconds: int,
) -> List[Dict[str, Any]]:
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(cookie_jar),
    )
    opener.addheaders = [("User-Agent", USER_AGENT)]

    page_url = urllib.parse.urljoin(base_url, page_path)
    with opener.open(page_url, timeout=timeout_seconds) as resp:
        resp.read()

    csrf_token = _extract_csrf(cookie_jar)
    data_path = SECURE_JSON_PATH.format(file_path=file_path)
    data_url = urllib.parse.urljoin(base_url, data_path)
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
        return json.loads(resp.read().decode("utf-8-sig"))


def _parse_pr_votes(payload: List[Dict[str, Any]]) -> List[PartyVote]:
    results: List[PartyVote] = []
    for item in payload:
        name = str(item.get("PoliticalPartyName", "")).strip()
        votes = int(float(item.get("TotalVoteReceived", 0) or 0))
        if name and votes > 0:
            results.append(PartyVote(name, votes))
    if not results:
        raise RuntimeError("No PR party vote data found in source payload.")
    return results


def _parse_fptp_results(payload: List[Dict[str, Any]]) -> List[FPTPPartyResult]:
    results: List[FPTPPartyResult] = []
    for item in payload:
        name = str(item.get("PoliticalPartyName", "")).strip()
        won = int(float(item.get("TotWin", 0) or 0))
        leading = int(float(item.get("TotLead", 0) or 0))
        total = int(float(item.get("TotWinLead", won + leading) or 0))
        if name and (won > 0 or leading > 0 or total > 0):
            results.append(FPTPPartyResult(name, won=won, leading=leading, total=total))
    if not results:
        raise RuntimeError("No FPTP party result data found in source payload.")
    return results


def _extract_csrf(cookie_jar: CookieJar) -> str:
    for cookie in cookie_jar:
        if cookie.name == "CsrfToken":
            return cookie.value
    raise RuntimeError("CsrfToken cookie not found")
