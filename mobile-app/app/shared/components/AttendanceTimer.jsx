/**
 * AttendanceTimer — displays the remaining time in the 2-minute attendance window.
 *
 * Shows a countdown ring that goes red when < 30 seconds remain.
 * Calls onExpire (and auto-resets attendance state) when time runs out.
 *
 * Usage:
 *   <AttendanceTimer onExpire={handleExpiry} />
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useCountdown } from '../hooks/useCountdown';
import { useAuthStore } from '../store/authStore';

export default function AttendanceTimer({ onExpire, style }) {
  const resetAttendance = useAuthStore((s) => s.resetAttendance);

  const handleExpire = () => {
    resetAttendance();
    if (onExpire) onExpire();
  };

  const { remaining, isExpired, formatted } = useCountdown({ onExpire: handleExpire });

  if (remaining === null) return null;

  const isUrgent = remaining !== null && remaining < 30;

  return (
    <View style={[styles.container, isUrgent && styles.urgent, style]}>
      <Text style={[styles.label, isUrgent && styles.labelUrgent]}>
        {isExpired ? 'Süre doldu — lütfen yeniden başlayın' : 'Kalan süre'}
      </Text>
      <Text style={[styles.time, isUrgent && styles.timeUrgent]}>{formatted}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#EEF2FF',
    borderWidth: 1,
    borderColor: '#6366F1',
  },
  urgent: {
    backgroundColor: '#FFF1F2',
    borderColor: '#F43F5E',
  },
  label: {
    fontSize: 11,
    color: '#6366F1',
    fontWeight: '500',
    marginBottom: 2,
  },
  labelUrgent: {
    color: '#F43F5E',
  },
  time: {
    fontSize: 28,
    fontWeight: '700',
    color: '#4F46E5',
    fontVariant: ['tabular-nums'],
  },
  timeUrgent: {
    color: '#F43F5E',
  },
});
