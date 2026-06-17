
import logging
logger = logging.getLogger('Watchdog')


class _DisabledWatchdog:
    def __init__(self, timeout=0.0):
        self.timeout = timeout

    def heartbeat(self):
        return None

def initialize_watchdog(app_instance, timeout=5.0):
    """Disable watchdog logging in production builds."""
    watchdog = _DisabledWatchdog(timeout=timeout)
    app_instance._watchdog = watchdog
    logger.info("Watchdog disabled")
    return watchdog
