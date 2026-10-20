// Deterministic token bucket lab; inject a monotonic clock instead of busy waiting.
(() => {
  function assert(condition, message) { if (!condition) throw new Error(message); }
  class TokenBucket {
    constructor(capacity, refillPerSecond, clock = () => performance.now()) {
      if (!Number.isFinite(capacity) || capacity <= 0 || !Number.isFinite(refillPerSecond) || refillPerSecond <= 0) throw new RangeError('Capacity and refill rate must be positive');
      this.capacity = capacity;
      this.tokens = capacity;
      this.refillPerSecond = refillPerSecond;
      this.clock = clock;
      this.lastRefill = clock();
    }
    refill() {
      const now = this.clock();
      const elapsed = Math.max(0, now - this.lastRefill) / 1000;
      this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.refillPerSecond);
      this.lastRefill = Math.max(now, this.lastRefill);
    }
    validate(tokens) {
      if (!Number.isFinite(tokens) || tokens <= 0) throw new RangeError('Requested tokens must be positive');
    }
    tryAcquire(tokens = 1) {
      this.validate(tokens);
      this.refill();
      if (tokens > this.tokens) return false;
      this.tokens -= tokens;
      return true;
    }
    waitTime(tokens = 1) {
      this.validate(tokens);
      this.refill();
      if (tokens > this.capacity) return Infinity;
      return Math.max(0, tokens - this.tokens) / this.refillPerSecond * 1000;
    }
  }
  let now = 0;
  const limiter = new TokenBucket(3, 10, () => now);
  assert([1, 2, 3].every(() => limiter.tryAcquire()), 'Initial burst is allowed');
  assert(!limiter.tryAcquire(), 'Fourth call is rejected');
  assert(limiter.waitTime() === 100, 'One token needs 100ms');
  now = 100;
  assert(limiter.tryAcquire(), 'One token refilled');
  now = 600;
  limiter.refill();
  assert(limiter.tokens === 3, 'Refill is capped at capacity');
  assert(limiter.waitTime(4) === Infinity, 'Oversized requests can never fit');
  let rejected = false;
  try { limiter.tryAcquire(-1); } catch { rejected = true; }
  assert(rejected, 'Negative requests must not create tokens');
  console.log('Token bucket assertions passed without real sleeps or a busy loop.');
  // Try changing capacity/refill and predicting the wait before advancing the clock.
})();
