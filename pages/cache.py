from datetime import datetime, timedelta
from pages.jsonstore import db

def getCache(user: str, name: str, expires: int, data):
    cache = {}
    if db.exists('user-cache', user):
        cache = db.get('user-cache', user);
    cache_data = cache.get(name)
    if not cache_data or cache_data.get('expires') < int(datetime.now().timestamp()):
        cache_data = data()
        cache[name] = { "expires": int((datetime.now() + timedelta(minutes=expires)).timestamp()), "data": cache_data}
        db.save('user-cache', user, cache)
        cache = cache_data
    else:
        # print('got {} from cache\nuser: {}'.format(name, user))
        cache = cache.get(name, {}).get('data')
    return cache