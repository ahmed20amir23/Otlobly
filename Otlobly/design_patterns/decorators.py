def logger(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Executing {func.__name__}")
        return func(*args, **kwargs)
    return wrapper