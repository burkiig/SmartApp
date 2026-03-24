/**
 * useCountdown — reactive countdown timer hook for the attendance flow.
 *
 * Ticks every second while there is an active attendance step.
 * Automatically calls onExpire when the window runs out.
 *
 * Usage:
 *   const { remaining, isExpired, formatted } = useCountdown({ onExpire: resetAttendance });
 */

import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../store/authStore';

/**
 * @param {{ onExpire?: () => void }} options
 * @returns {{ remaining: number|null, isExpired: boolean, formatted: string }}
 */
export function useCountdown({ onExpire } = {}) {
  const getRemainingSeconds = useAuthStore((s) => s.getRemainingSeconds);
  const stepStartedAt = useAuthStore((s) => s.attendanceState.stepStartedAt);

  const [remaining, setRemaining] = useState(() => getRemainingSeconds());
  const onExpireRef = useRef(onExpire);
  onExpireRef.current = onExpire;

  useEffect(() => {
    if (!stepStartedAt) {
      setRemaining(null);
      return;
    }

    const tick = () => {
      const secs = getRemainingSeconds();
      setRemaining(secs);
      if (secs === 0 && onExpireRef.current) {
        onExpireRef.current();
      }
    };

    tick(); // immediate first tick
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [stepStartedAt, getRemainingSeconds]);

  const isExpired = remaining === 0;

  // Format as MM:SS
  const formatted =
    remaining === null
      ? '--:--'
      : `${String(Math.floor(remaining / 60)).padStart(2, '0')}:${String(remaining % 60).padStart(2, '0')}`;

  return { remaining, isExpired, formatted };
}
