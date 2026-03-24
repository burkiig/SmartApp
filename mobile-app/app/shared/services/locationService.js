import * as Location from 'expo-location';
import apiAdapter from '../utils/apiAdapter';

/**
 * Request foreground location permission from the user.
 * @returns {{ granted: boolean, canAskAgain: boolean }}
 */
export const requestLocationPermission = async () => {
  const { status, canAskAgain } = await Location.requestForegroundPermissionsAsync();
  return {
    granted: status === 'granted',
    canAskAgain
  };
};

/**
 * Check whether foreground location permission is already granted
 * without prompting the user.
 * @returns {boolean}
 */
export const hasLocationPermission = async () => {
  const { status } = await Location.getForegroundPermissionsAsync();
  return status === 'granted';
};

/**
 * Get the device's current GPS coordinates.
 * Returns the full Location object so callers can access mocked, altitude, etc.
 *
 * @param {{ accuracy?: Location.Accuracy, timeout?: number }} options
 * @returns {Location.LocationObject}
 */
export const getCurrentLocation = async (options = {}) => {
  const granted = await hasLocationPermission();
  if (!granted) {
    const { granted: nowGranted } = await requestLocationPermission();
    if (!nowGranted) {
      throw new Error('Konum izni verilmedi. Ayarlardan izin verin.');
    }
  }

  return await Location.getCurrentPositionAsync({
    accuracy: options.accuracy ?? Location.Accuracy.High,
    timeInterval: options.timeout ?? 10000,
  });
};

/**
 * Normalize speed value.
 * iOS returns -1 when speed is unavailable; normalize to null.
 * @param {number|null|undefined} rawSpeed
 * @returns {number|null}
 */
const normalizeSpeed = (rawSpeed) => {
  if (rawSpeed == null || rawSpeed < 0) return null;
  return rawSpeed;
};

/**
 * Verify that the student is inside the classroom geofence.
 * Calls the Flask backend's POST /api/verify/location endpoint.
 *
 * Sends full GPS metadata so the backend can apply all heuristic checks:
 *   - mocked flag (OS-level mock GPS detection)
 *   - accuracy anomaly (< 5m is suspiciously precise)
 *   - altitude zero (mock GPS apps omit altitude)
 *   - speed spike
 *   - GPS timestamp vs server receive time
 *
 * @param {string} sessionId  - Active attendance session UUID
 * @returns {{
 *   inside: boolean,
 *   distance_m: number|null,
 *   geofence_radius: number|null,
 *   room_name: string,
 *   step_id: string,
 *   is_flagged: boolean,
 *   flag_reason: string|null
 * }}
 */
export const verifyLocation = async (sessionId) => {
  const location = await getCurrentLocation();
  const { coords } = location;

  const payload = {
    session_id: sessionId,
    latitude: coords?.latitude,
    longitude: coords?.longitude,
    accuracy: coords?.accuracy ?? null,
    altitude: coords?.altitude ?? null,
    speed: normalizeSpeed(coords?.speed),
    // GPS fix timestamp from device (ISO string) — used for replay attack detection
    gps_timestamp: location.timestamp
      ? new Date(location.timestamp).toISOString()
      : null,
    // Expo SDK 48+: OS-level mock GPS flag
    mocked: location.mocked ?? false,
  };

  const result = await apiAdapter.post('/verify/location', payload);

  return {
    ...result,
    // Echo back raw coords for UI display
    latitude: coords?.latitude,
    longitude: coords?.longitude,
    gps_accuracy: coords?.accuracy,
  };
};
