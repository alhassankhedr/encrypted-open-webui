/**
 * Lorica encryption integration for Open WebUI
 * Main entry point for Lorica functionality
 */

export { LoricaSession, getLoricaSession, loricaFetch } from './session';
export { Attestor } from './attestor';
export { isLoricaBackend, shouldUseLoricaEncryption, clearDetectionCache } from './detector';
export { 
  encapsulateRequest, 
  decapsulateResponse, 
  parseKeyConfig,
  parseEncapsulatedRequest,
  createStreamingResponse
} from './ohttp';

export type {
  OHTTPKeyConfig,
  JWTPayload,
  TCBStatus,
  AttestationReport,
  LoricaConfig,
  CacheEntry,
  LoricaSessionOptions,
  OHTTPRequest,
  OHTTPResponse,
  AttestationError,
  OHTTPError,
  JWTValidationError
} from './types';

// Re-export for convenience
export { loricaFetch as fetch } from './session';
