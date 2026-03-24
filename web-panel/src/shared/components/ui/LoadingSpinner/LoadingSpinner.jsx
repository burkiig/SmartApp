import './LoadingSpinner.css';

/**
 * LoadingSpinner — animated circular indicator.
 *
 * @param {('sm'|'md'|'lg')} size
 * @param {string} className
 */
export function LoadingSpinner({ size = 'md', className = '' }) {
  return (
    <div className={`loading-spinner-overlay ${className}`}>
      <div className={`loading-spinner loading-spinner--${size}`} role="status" aria-label="Loading" />
    </div>
  );
}

export default LoadingSpinner;
