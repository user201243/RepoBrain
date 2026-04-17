from app.services.retry_handler import process_retry_queue


def payment_retry_job() -> list[dict[str, object]]:
    return process_retry_queue()


def register_cron_job(scheduler: object) -> None:
    scheduler.schedule("*/5 * * * *", payment_retry_job)
