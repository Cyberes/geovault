from datetime import datetime


def create_import_log_msg(msg: str):
    return datetime.now().isoformat(), msg
