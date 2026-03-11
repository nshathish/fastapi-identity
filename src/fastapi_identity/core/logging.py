import logging
import sys

# ANSI color codes (only used when output is a TTY)
_RESET = "\033[0m"
_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",    # cyan
    logging.INFO: "\033[32m",     # green
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",     # red
    logging.CRITICAL: "\033[1;31m",  # bold red
}


class ColoredFormatter(logging.Formatter):
    """Formatter that colors the entire log line by level when the stream is a TTY."""

    def __init__(self, fmt: str, use_color: bool | None = None, **kwargs) -> None:
        super().__init__(fmt, **kwargs)
        self._use_color = use_color if use_color is not None else sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        out = super().format(record)
        if self._use_color and record.levelno in _LEVEL_COLORS:
            return f"{_LEVEL_COLORS[record.levelno]}{out}{_RESET}"
        return out


def setup_logging(use_color: bool | None = None) -> logging.Logger:
    logger = logging.getLogger("fastapi_template_project")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = ColoredFormatter(fmt, use_color=use_color)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"fastapi_template_project.{name}")
    return logging.getLogger("fastapi_template_project")
