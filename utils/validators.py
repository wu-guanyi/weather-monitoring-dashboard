def validate_city(city, allowed_cities):
    if not city:
        return False, "缺少 city 參數"

    if city not in allowed_cities:
        return False, f"不支援的城市：{city}"

    return True, None


def validate_limit(limit, default=10, max_limit=100):
    try:
        limit = int(limit)
        if limit <= 0:
            return False, "limit 必須大於 0", default
        if limit > max_limit:
            return False, f"limit 不可大於 {max_limit}", default
        return True, None, limit
    except (TypeError, ValueError):
        return False, "limit 必須是整數", default