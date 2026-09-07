class CacheService:
    def __init__(self):
        self._cache = {}

    def _normalize_key(self, key: str) -> str:
        return key.strip().lower()

    def get(self, key: str) -> str:
        return self._cache.get(self._normalize_key(key))

    def set(self, key: str, value: str):
        self._cache[self._normalize_key(key)] = value

class MetricsService:
    def __init__(self):
        self.processed_queries = 0
        self.escalated_queries = 0
        self.cache_hits = 0
        self.total_cost_usd = 0.0
        
        # Rough estimation for GPT-3.5-Turbo costs (Input: $0.0005/1K, Output: $0.0015/1K)
        self.cost_per_input_token = 0.0005 / 1000
        self.cost_per_output_token = 0.0015 / 1000

    def record_query(self):
        self.processed_queries += 1

    def record_escalation(self):
        self.escalated_queries += 1

    def record_cache_hit(self):
        self.cache_hits += 1

    def record_tokens(self, input_tokens: int = 0, output_tokens: int = 0):
        self.total_cost_usd += (input_tokens * self.cost_per_input_token) + (output_tokens * self.cost_per_output_token)

    def reset(self):
        self.processed_queries = 0
        self.escalated_queries = 0
        self.cache_hits = 0
        self.total_cost_usd = 0.0

    def get_metrics(self) -> dict:
        escalation_rate = (self.escalated_queries / self.processed_queries) if self.processed_queries > 0 else 0.0
        return {
            "processedQueries": self.processed_queries,
            "escalatedQueries": self.escalated_queries,
            "escalationRate": f"{escalation_rate:.2f}",
            "cacheHits": self.cache_hits,
            "totalCostUSD": f"{self.total_cost_usd:.4f}"
        }

cache_service = CacheService()
metrics_service = MetricsService()
