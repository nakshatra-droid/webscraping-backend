import re


class QueryFilterUtils:
    @staticmethod
    def parse_query_filters(query: str) -> tuple[str, dict]:
        """
        Extract simple numeric filters from a text query string.
        """
        filters: dict = {}
        q = query.lower()

        # price upper bound
        m = re.search(
            r"(?:under|below|less than|upto|up to)\s*₹?\s*(\d+(?:,\d+)*(?:k)?)", q
        )
        if m:
            raw = m.group(1).replace(",", "")
            val = float(raw[:-1]) * 1000 if raw.endswith("k") else float(raw)
            filters["price_max"] = val
            q = q[: m.start()] + q[m.end() :]

        # price lower bound
        m = re.search(
            r"(?:above|over|more than|minimum|min)\s*₹?\s*(\d+(?:,\d+)*(?:k)?)", q
        )
        if m:
            raw = m.group(1).replace(",", "")
            val = float(raw[:-1]) * 1000 if raw.endswith("k") else float(raw)
            filters["price_min"] = val
            q = q[: m.start()] + q[m.end() :]

        # minimum rating
        m = re.search(
            r"(?:rating\s*(?:of\s*)?|at least\s*|min(?:imum)?\s*rating\s*)(\d+(?:\.\d+)?)",
            q,
        )
        if m:
            filters["rating_min"] = float(m.group(1))
            q = q[: m.start()] + q[m.end() :]

        # best and top rated
        if re.search(r"\b(best|top rated|highest rated|top pick|most popular)\b", q):
            filters["sort_by_rating"] = True
            filters.setdefault("rating_min", 4.0)
            q = re.sub(
                r"\b(best|top rated|highest rated|top pick|most popular)\b", "", q
            )

        # cheapest budget
        if re.search(
            r"\b(cheapest|budget|affordable|lowest price|cheap|inexpensive)\b", q
        ):
            filters["sort_by_price_asc"] = True
            q = re.sub(
                r"\b(cheapest|budget|affordable|lowest price|cheap|inexpensive)\b",
                "",
                q,
            )

        # specific discount percentage
        m = re.search(
            r"(?:min(?:imum)?\s*)?(\d+(?:\.\d+)?)\s*%\s*(?:off|discount|sale)", q
        )
        if m:
            filters["discount_min"] = float(m.group(1))
            q = q[: m.start()] + q[m.end() :]

        # general discount keywords without a specific percentage
        elif re.search(
            r"\b(discounted|on sale|with discount|big discount|sale|offers?|deal)\b", q
        ):
            filters["discount_min"] = 5.0
            q = re.sub(
                r"\b(discounted|on sale|with discount|big discount|sale|offers?|deal)\b",
                "",
                q,
            )

        cleaned = " ".join(q.split()).strip()
        return cleaned, filters
