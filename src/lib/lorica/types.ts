/**
 * TypeScript type definitions for Lorica encryption integration
 * Based on the Python Lorica package implementation
 */

export interface OHTTPKeyConfig {
  /** The OHTTP key configuration as bytes (hex-encoded) */
  keyConfig: Uint8Array;
  /** The key identifier */
  keyId: number;
  /** The HPKE suite identifier */
  suiteId: number;
}

export interface JWTPayload {
  /** Token expiration timestamp */
  exp: number;
  /** Issued at timestamp */
  iat: number;
  /** TCB status containing PCR values */
  'tcb-status': string;
  /** Additional claims */
  [key: string]: any;
}

export interface TCBStatus {
  /** PCR values from the attestation report */
  [pcrKey: string]: string;
}

export interface AttestationReport {
  /** The JWT token */
  token: string;
  /** The parsed TCB status */
  tcbStatus: TCBStatus;
  /** The OHTTP key configuration */
  keyConfig: Uint8Array;
}

export interface LoricaConfig {
  /** Master toggle for Lorica encryption */
  enabled: boolean;
  /** Trustee URL for attestation validation */
  trusteeUrl: string;
  /** Whether to perform attestation checks */
  attestationEnabled: boolean;
  /** List of known Lorica backend URLs */
  backendUrls: string[];
}

export interface CacheEntry<T> {
  /** The cached value */
  value: T;
  /** Timestamp when cached */
  timestamp: number;
  /** Time to live in milliseconds */
  ttl: number;
}

export interface LoricaSessionOptions {
  /** Trustee URL for attestation */
  trusteeUrl?: string;
  /** Whether to perform attestation */
  attest?: boolean;
}

export interface OHTTPRequest {
  /** The encapsulated request data */
  data: Uint8Array;
  /** The key identifier used */
  keyId: number;
}

export interface OHTTPResponse {
  /** The decapsulated response data */
  data: Uint8Array;
  /** The key identifier used */
  keyId: number;
}

/** Error thrown when attestation fails */
export class AttestationError extends Error {
  constructor(message: string, public cause?: Error) {
    super(message);
    this.name = 'AttestationError';
  }
}

/** Error thrown when OHTTP operations fail */
export class OHTTPError extends Error {
  constructor(message: string, public cause?: Error) {
    super(message);
    this.name = 'OHTTPError';
  }
}

/** Error thrown when JWT validation fails */
export class JWTValidationError extends Error {
  constructor(message: string, public cause?: Error) {
    super(message);
    this.name = 'JWTValidationError';
  }
}
