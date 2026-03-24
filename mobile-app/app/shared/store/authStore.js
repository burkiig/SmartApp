/**
 * Auth Store — global authentication state (Zustand).
 *
 * Stores the current user, JWT token, and the 3-step attendance progress.
 * Token is persisted in expo-secure-store (encrypted on-device storage).
 *
 * Usage:
 *   import { useAuthStore } from '../shared/store/authStore';
 *   const { user, isAuthenticated, login, logout } = useAuthStore();
 */

import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import { API_URL } from '../config/env';

const TOKEN_KEY = 'auth_access_token';
const REFRESH_KEY = 'auth_refresh_token';

export const useAuthStore = create((set, get) => ({
  // ── Auth state ─────────────────────────────────────────────────────────────
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,   // true during initial token restoration

  // ── Attendance 3-step state ────────────────────────────────────────────────
  attendanceState: {
    stepId: null,         // returned by /api/verify/location (Step 1)
    sessionId: null,
    gpsVerified: false,
    gpsDistance: null,
    faceVerified: false,
    faceScore: null,
    stepStartedAt: null,  // ISO string — used to show remaining time to user
  },

  // ── Login ──────────────────────────────────────────────────────────────────
  /**
   * Authenticate with the backend and persist tokens securely.
   * @param {string} username
   * @param {string} password
   * @returns {{ success: boolean, error?: string }}
   */
  login: async (username, password) => {
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();

      if (!data.success) {
        return { success: false, error: data.message || 'Giriş başarısız' };
      }

      await SecureStore.setItemAsync(TOKEN_KEY, data.access_token);
      if (data.refresh_token) {
        await SecureStore.setItemAsync(REFRESH_KEY, data.refresh_token);
      }

      set({ user: data.user, token: data.access_token, isAuthenticated: true });
      return { success: true };
    } catch (err) {
      return { success: false, error: 'Sunucuya bağlanılamadı' };
    }
  },

  // ── Logout ─────────────────────────────────────────────────────────────────
  logout: async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(REFRESH_KEY);
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      attendanceState: get()._defaultAttendanceState(),
    });
  },

  // ── Restore session on app start ───────────────────────────────────────────
  /**
   * Called once in the root layout (_layout.js) via useEffect.
   * Reads the stored token, verifies it against /api/auth/me (or similar),
   * and restores the session if valid.
   */
  restoreSession: async () => {
    set({ isLoading: true });
    try {
      const token = await SecureStore.getItemAsync(TOKEN_KEY);
      if (!token) {
        set({ isLoading: false });
        return;
      }

      // Verify token against server
      const response = await fetch(`${API_URL}/users`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        // Token valid — we don't have user data here, keep token and mark authenticated
        // A /api/auth/me endpoint would be ideal; for now use stored token
        set({ token, isAuthenticated: true });
      } else {
        // Try refresh
        await get().refreshToken();
      }
    } catch {
      // Network error — keep user logged in with stored token (offline support)
      const token = await SecureStore.getItemAsync(TOKEN_KEY);
      if (token) set({ token, isAuthenticated: true });
    } finally {
      set({ isLoading: false });
    }
  },

  // ── Token refresh ──────────────────────────────────────────────────────────
  refreshToken: async () => {
    try {
      const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY);
      if (!refreshToken) return false;

      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${refreshToken}`,
        },
      });
      const data = await response.json();

      if (data.success && data.access_token) {
        await SecureStore.setItemAsync(TOKEN_KEY, data.access_token);
        set({ token: data.access_token, isAuthenticated: true });
        return true;
      }

      await get().logout();
      return false;
    } catch {
      return false;
    }
  },

  // ── Attendance step management ─────────────────────────────────────────────
  startAttendance: (sessionId) => set({
    attendanceState: {
      stepId: null,
      sessionId,
      gpsVerified: false,
      gpsDistance: null,
      faceVerified: false,
      faceScore: null,
      stepStartedAt: new Date().toISOString(),
    },
  }),

  setGpsVerified: (stepId, distanceM) => set((state) => ({
    attendanceState: {
      ...state.attendanceState,
      stepId,
      gpsVerified: true,
      gpsDistance: distanceM,
    },
  })),

  setFaceVerified: (faceScore) => set((state) => ({
    attendanceState: {
      ...state.attendanceState,
      faceVerified: true,
      faceScore,
    },
  })),

  resetAttendance: () => set((state) => ({
    attendanceState: state._defaultAttendanceState(),
  })),

  /** @private */
  _defaultAttendanceState: () => ({
    stepId: null,
    sessionId: null,
    gpsVerified: false,
    gpsDistance: null,
    faceVerified: false,
    faceScore: null,
    stepStartedAt: null,
  }),

  // ── Selectors ──────────────────────────────────────────────────────────────
  getAuthHeader: () => {
    const { token } = get();
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  isStepExpired: () => {
    const { stepStartedAt } = get().attendanceState;
    if (!stepStartedAt) return false;
    const elapsed = (Date.now() - new Date(stepStartedAt).getTime()) / 1000;
    return elapsed > 120; // 2-minute window (must match ATTENDANCE_STEP_TIMEOUT_SECONDS)
  },

  /**
   * Returns remaining seconds in the 2-minute attendance window.
   * Returns null when no active step.
   * Use with useCountdown hook for reactive UI.
   */
  getRemainingSeconds: () => {
    const { stepStartedAt } = get().attendanceState;
    if (!stepStartedAt) return null;
    const elapsed = (Date.now() - new Date(stepStartedAt).getTime()) / 1000;
    return Math.max(0, Math.floor(120 - elapsed));
  },
}));
