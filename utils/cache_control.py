from django.core.cache import cache


def make_cache_key(model, key: str) -> str:
    return f"{model.__name__}-{key}"


def set_cache_code_by_name(model, key: str):
    _name = model.get_queryset(code=key).first()
    if _name:
        cache.set(make_cache_key(model, key), _name, timeout=None)


def get_cache_code_by_name(model, key: str):
    _key = make_cache_key(model, key)

    _cd = cache.get(_key)
    if not _cd:
        set_cache_code_by_name(model, key)
        _cd = cache.get(_key)
    return _cd
