import httpx

WIKIPEDIA_SUMMARY_URL = "https://tr.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKIPEDIA_SEARCH_URL = "https://tr.wikipedia.org/w/api.php"

REQUEST_TIMEOUT = 10.0


async def fetch_topic_summary(topic: str) -> dict:
    """
    Wikipedia REST API'den verilen konu için özet bilgi çeker.
    Pazar büyüklüğü tahmini ve sektör bağlamı için kullanılır.
    """
    if not topic or not topic.strip():
        return {"found": False, "error": "Empty topic"}

    title = topic.strip().replace(" ", "_")
    url = WIKIPEDIA_SUMMARY_URL.format(title=title)

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url, headers={"User-Agent": "ai-startup-mentor/1.0"})
            if response.status_code == 404:
                return {"found": False, "error": "Topic not found"}
            response.raise_for_status()
            data = response.json()

            return {
                "found": True,
                "title": data.get("title"),
                "description": data.get("description"),
                "extract": data.get("extract"),
                "url": (data.get("content_urls") or {}).get("desktop", {}).get("page"),
            }
    except httpx.HTTPError as exc:
        return {"found": False, "error": f"HTTP error: {exc}"}
    except Exception as exc:
        return {"found": False, "error": str(exc)}


async def search_competitors(query: str, limit: int = 5) -> list[dict]:
    """
    Wikipedia arama API'si ile verilen sektör/anahtar kelime için
    potansiyel rakip/şirket adaylarını döner.
    """
    if not query or not query.strip():
        return []

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query.strip(),
        "srlimit": max(1, min(limit, 20)),
        "utf8": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(
                WIKIPEDIA_SEARCH_URL,
                params=params,
                headers={"User-Agent": "ai-startup-mentor/1.0"},
            )
            response.raise_for_status()
            data = response.json()

            items = (data.get("query") or {}).get("search") or []
            return [
                {
                    "title": item.get("title"),
                    "snippet": item.get("snippet"),
                    "pageid": item.get("pageid"),
                }
                for item in items
            ]
    except httpx.HTTPError:
        return []
    except Exception:
        return []


async def gather_market_context(topic: str) -> dict:
    """
    Tek çağrıda hem konu özetini hem de potansiyel rakip listesini döner.
    AI veya kullanıcı arayüzü tarafından zenginleştirme için kullanılabilir.
    """
    summary = await fetch_topic_summary(topic)
    competitors = await search_competitors(topic, limit=5)
    return {
        "topic": topic,
        "summary": summary,
        "competitors": competitors,
    }
