const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const withRetry = async (fn, retries = 3, delay = 1000) => {
  let lastError;
  
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (i < retries - 1) {
        await wait(delay * Math.pow(2, i)); // Exponential backoff
        continue;
      }
      throw lastError;
    }
  }
};