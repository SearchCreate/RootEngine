#返回 UTC 的 ISO 格式的时间
from datetime import datetime, timezone

def get_iso_timestamp(microseconds=True):
    """自定义是否包含微秒"""
    if microseconds:
        return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')
    else:
        return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
