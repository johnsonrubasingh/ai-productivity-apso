from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class MetricsRegistry:
    request_total: Counter[tuple[str, str, str]] = field(default_factory=Counter)
    request_duration_ms_sum: Counter[tuple[str, str, str]] = field(default_factory=Counter)
    lock: Lock = field(default_factory=Lock)

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        status_class = f"{status_code // 100}xx"
        key = (method.upper(), path, status_class)
        with self.lock:
            self.request_total[key] += 1
            self.request_duration_ms_sum[key] += int(duration_ms)

    def render_prometheus(self) -> str:
        lines = [
            "# HELP apso_http_requests_total Total HTTP requests by method, path, and status class.",
            "# TYPE apso_http_requests_total counter",
        ]
        with self.lock:
            for (method, path, status_class), value in sorted(self.request_total.items()):
                lines.append(
                    'apso_http_requests_total{'
                    f'method="{method}",path="{path}",status_class="{status_class}"'
                    f"}} {value}"
                )

            lines.extend(
                [
                    "# HELP apso_http_request_duration_ms_sum Sum of HTTP request duration in milliseconds.",
                    "# TYPE apso_http_request_duration_ms_sum counter",
                ]
            )
            for (method, path, status_class), value in sorted(self.request_duration_ms_sum.items()):
                lines.append(
                    'apso_http_request_duration_ms_sum{'
                    f'method="{method}",path="{path}",status_class="{status_class}"'
                    f"}} {value}"
                )
        return "\n".join(lines) + "\n"


metrics_registry = MetricsRegistry()
