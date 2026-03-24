import './Input.css';

/**
 * Input — controlled text input with label and error state.
 *
 * @param {string}   label
 * @param {string}   error      — validation error message
 * @param {string}   className
 * @param props                 — all other props forwarded to <input>
 */
export function Input({ label, error, className = '', ...props }) {
  return (
    <div className={`input-wrapper ${className}`}>
      {label && (
        <label className="input-label" htmlFor={props.id}>
          {label}
        </label>
      )}
      <input
        className={`input-field${error ? ' input-field--error' : ''}`}
        {...props}
      />
      {error && <span className="input-error-message">{error}</span>}
    </div>
  );
}

export default Input;
