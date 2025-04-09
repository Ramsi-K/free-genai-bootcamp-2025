class CacheService {
  constructor() {
    this.cache = new Map();
    this.expiryTimes = new Map();
  }

  set(key, value, ttlMinutes = 5) {
    this.cache.set(key, value);
    this.expiryTimes.set(key, Date.now() + (ttlMinutes * 60 * 1000));
  }

  get(key) {
    if (!this.cache.has(key)) return null;
    if (Date.now() > this.expiryTimes.get(key)) {
      this.delete(key);
      return null;
    }
    return this.cache.get(key);
  }

  delete(key) {
    this.cache.delete(key);
    this.expiryTimes.delete(key);
  }

  clear() {
    this.cache.clear();
    this.expiryTimes.clear();
  }
}

export const cacheService = new CacheService();