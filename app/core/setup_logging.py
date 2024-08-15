import logging

import posthog

from app.core.settings import settings


def setup_logging(name=None, celery=False):
    # Configure PostHog
    posthog.project_api_key = settings.posthog_api_key
    posthog.host = settings.posthog_host

    logger = logging.getLogger(name or __name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    # Custom logging handler to send logs to PostHog
    # class PostHogHandler(logging.Handler):
    #     def emit(self, record):
    #         log_entry = self.format(record)
    #         posthog.capture(distinct_id="logger", event="log_event", properties={"message": log_entry})
    #
    # posthog_handler = PostHogHandler()
    # posthog_handler.setLevel(logging.INFO)
    # posthog_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    # logger.addHandler(posthog_handler)

    if celery:
        from celery.utils.log import get_logger
        logger = get_logger(__name__)
        # logger.addHandler(posthog_handler)
        logger.addHandler(handler)

    return logger
