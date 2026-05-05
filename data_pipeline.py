"""
Data Pipeline — Real Data Fetcher Module
=========================================
This module is included in every generated API. It fetches real data
from public sources and caches it in-memory with TTL.
"""

import json
import time
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone


class DataFetcher:
    """Fetches and caches data from public APIs with TTL."""

    def __init__(self, source_configs=None):
        self.cache = {}
        self.default_ttl = 300  # 5 minutes default
        self.sources = source_configs or {}

    def fetch(self, url, ttl=None):
        """Fetch JSON from a URL with caching."""
        cache_key = hashlib.md5(url.encode()).hexdigest()
        now = time.time()
        effective_ttl = ttl or self.default_ttl

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if now - entry["cached_at"] < effective_ttl:
                return entry["data"]

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "DataPipeline/1.0 (API Product)"
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                self.cache[cache_key] = {"data": data, "cached_at": now}
                return data
        except Exception as e:
            # If stale cache exists, return it
            if cache_key in self.cache:
                return self.cache[cache_key]["data"]
            return {"error": str(e), "data": []}

    def fetch_text(self, url, ttl=None):
        """Fetch raw text from a URL with caching."""
        cache_key = hashlib.md5(f"text:{url}".encode()).hexdigest()
        now = time.time()
        effective_ttl = ttl or self.default_ttl

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if now - entry["cached_at"] < effective_ttl:
                return entry["data"]

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "DataPipeline/1.0 (API Product)"
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                text = resp.read().decode()
                self.cache[cache_key] = {"data": text, "cached_at": now}
                return text
        except Exception as e:
            if cache_key in self.cache:
                return self.cache[cache_key]["data"]
            return ""

    # ── Category-Specific Data Sources ───────────────────────────

    def fetch_hn_stories(self, limit=30):
        """Fetch top Hacker News stories with their details."""
        data = self.fetch(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            ttl=300
        )
        if isinstance(data, dict) and "error" in data:
            return []

        stories = []
        for sid in (data or [])[:limit]:
            story = self.fetch(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                ttl=3600
            )
            if isinstance(story, dict) and "title" in story:
                stories.append({
                    "id": story.get("id"),
                    "title": story.get("title", ""),
                    "url": story.get("url", ""),
                    "score": story.get("score", 0),
                    "by": story.get("by", ""),
                    "time": datetime.fromtimestamp(
                        story.get("time", 0), tz=timezone.utc
                    ).isoformat() if story.get("time") else None
                })
        return stories

    def fetch_fda_recalls(self, limit=50):
        """Fetch FDA drug recall/enforcement reports."""
        data = self.fetch(
            f"https://api.fda.gov/drug/enforcement.json?limit={limit}",
            ttl=3600
        )
        if isinstance(data, dict) and "error" in data:
            return []
        results = data.get("results", []) if isinstance(data, dict) else []
        return [{
            "recall_number": r.get("recall_number", ""),
            "product": r.get("product_description", ""),
            "reason": r.get("reason_for_recall", ""),
            "classification": r.get("classification", ""),
            "firm": r.get("recalling_firm", ""),
            "date": r.get("report_date", ""),
            "status": r.get("status", "")
        } for r in results[:limit]]

    def fetch_open_food_products(self, limit=30):
        """Fetch product data from Open Food Facts."""
        data = self.fetch(
            f"https://world.openfoodfacts.org/api/v2/search?"
            f"fields=code,product_name,brands,categories_tags,nutriscore_grade"
            f"&size={limit}",
            ttl=7200
        )
        if isinstance(data, dict) and "error" in data:
            return []
        products = data.get("products", []) if isinstance(data, dict) else []
        return [{
            "barcode": p.get("code", ""),
            "name": p.get("product_name", ""),
            "brand": p.get("brands", ""),
            "categories": p.get("categories_tags", []),
        } for p in products[:limit]]

    def fetch_github_trending(self, language=None):
        """Scrape GitHub trending repos."""
        url = "https://api.github.com/search/repositories"
        query = "created:>2025-01-01 stars:>100"
        if language:
            query += f"+language:{language}"
        data = self.fetch(
            f"{url}?q={query}&sort=stars&order=desc&per_page=25",
            ttl=3600
        )
        if isinstance(data, dict) and "error" in data:
            return []
        items = data.get("items", []) if isinstance(data, dict) else []
        return [{
            "name": r.get("full_name", ""),
            "description": r.get("description", ""),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "language": r.get("language", ""),
            "url": r.get("html_url", ""),
            "topics": r.get("topics", []),
        } for r in items[:25]]
