class SessionManager {
  static STORAGE_KEY = 'korean_listening_practice_session';

  static saveSession(session) {
    try {
      localStorage.setItem(
        this.STORAGE_KEY,
        JSON.stringify({ ...session, timestamp: Date.now() })
      );
    } catch (error) {
      console.error('Failed to save session:', error);
    }
  }

  static loadSession() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (!saved) return null;

      const session = JSON.parse(saved);
      // Clear if older than 24 hours
      if (Date.now() - session.timestamp > 24 * 60 * 60 * 1000) {
        this.clearSession();
        return null;
      }
      return session;
    } catch (error) {
      console.error('Failed to load session:', error);
      return null;
    }
  }

  static clearSession() {
    localStorage.removeItem(this.STORAGE_KEY);
  }
}

export default SessionManager;