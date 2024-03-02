import logging


def configure_logger(level=logging.INFO, log_to_terminal=True, log_to_file=False, file_path='logs.txt'):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
                                  datefmt="%d-%m-%Y %H:%M:%S")

    if log_to_terminal:
        terminal_handler = logging.StreamHandler()
        terminal_handler.setLevel(logging.DEBUG)
        terminal_handler.setFormatter(formatter)
        logger.addHandler(terminal_handler)

    if log_to_file:
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def validate_password_len(pwd: str):
    if len(pwd) < 8:
        raise ValueError(f"Password {pwd} too short")
