import contextvars
import logging

trace_id_var = contextvars.ContextVar("trace_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)


def set_trace_id(trace_id: str):
    trace_id_var.set(trace_id)


def get_trace_id():
    return trace_id_var.get()


def set_user_id(user_id: str):
    user_id_var.set(user_id)


def get_user_id():
    return user_id_var.get()

class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        record.user_id = get_user_id()
        return True