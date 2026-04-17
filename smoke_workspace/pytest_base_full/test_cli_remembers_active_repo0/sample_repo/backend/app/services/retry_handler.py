retry_queue: list[dict[str, object]] = []


def enqueue_payment_retry(failed_payment: dict[str, object]) -> dict[str, object]:
    retry_count = int(failed_payment.get("retry_count", 0)) + 1
    failed_payment["retry_count"] = retry_count
    retry_queue.append(failed_payment)
    return failed_payment


def process_retry_queue() -> list[dict[str, object]]:
    processed: list[dict[str, object]] = []
    for item in retry_queue:
        processed.append({"status": "retried", "retry_count": item["retry_count"]})
    return processed
