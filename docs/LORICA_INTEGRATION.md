# Lorica Encryption Integration

## Overview

This document describes the integration of Lorica encryption into Open WebUI, enabling encrypted AI inference requests directly from the browser using the OHTTP (Oblivious HTTP) protocol with full attestation support.

## Features

- **Automatic Encryption**: Requests to Lorica backends are automatically encrypted using OHTTP
- **Attestation Support**: Full JWT validation and PCR checks for enhanced security
- **Streaming Support**: Compatible with AI chat streaming responses
- **Fallback Handling**: Graceful fallback to unencrypted requests if encryption fails
- **Configuration UI**: Easy-to-use settings interface for managing Lorica backends

## Architecture

### Core Components

1. **OHTTP Implementation** (`src/lib/lorica/ohttp/`)
   - HPKE-based encryption/decryption
   - Request/response encapsulation
   - Key configuration parsing

2. **Attestor** (`src/lib/lorica/attestor.ts`)
   - JWT token validation
   - Trustee service communication
   - PCR verification for security

3. **Session Wrapper** (`src/lib/lorica/session.ts`)
   - Transparent fetch API replacement
   - Automatic backend detection
   - Caching and error handling

4. **Settings UI** (`src/lib/components/admin/Settings/Lorica.svelte`)
   - Configuration management
   - Attestation status checking
   - Backend URL management

## Configuration

### Settings

Access Lorica settings through Admin → Settings → Lorica

- **Enable Lorica Encryption**: Master toggle for the feature
- **Trustee URL**: URL of the Trustee service (default: https://trustee.lorica.ai)
- **Enable Attestation**: Toggle JWT validation and PCR checks
- **Backend URLs**: List of known Lorica backend URLs

### Automatic Detection

The system automatically detects Lorica backends by:
1. Probing the `/discover` endpoint
2. Validating the OHTTP key configuration response
3. Caching results for performance

## Security Considerations

### Attestation Flow

1. **Key Config Fetch**: Retrieve OHTTP public key from `/discover`
2. **Token Fetch**: Get JWT attestation token from `/token`
3. **Trustee Validation**: Validate token with Trustee service
4. **PCR Verification**: Verify key matches attested enclave via PCR13

### Encryption

- Uses HPKE (Hybrid Public Key Encryption) for request encryption
- OHTTP protocol ensures end-to-end encryption
- Keys are cached with TTL for performance

## Usage

### For Users

1. Enable Lorica encryption in settings
2. Add your Lorica backend URLs
3. Configure Trustee URL if using custom deployment
4. Test attestation status using the "Check Status" button

### For Developers

```typescript
import { loricaFetch } from '$lib/lorica';

// Use loricaFetch instead of standard fetch
const response = await loricaFetch('https://your-lorica-backend.com/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello' })
});
```

## Troubleshooting

### Common Issues

1. **Attestation Fails**
   - Check Trustee URL is accessible
   - Verify backend is properly configured
   - Check network connectivity

2. **Encryption Errors**
   - Ensure backend supports OHTTP
   - Check key configuration is valid
   - Verify HPKE compatibility

3. **Performance Issues**
   - Clear attestation cache
   - Check TTL settings
   - Monitor network latency

### Debug Information

Enable browser console logging to see:
- Encryption status for each request
- Attestation validation results
- Cache hit/miss information
- Error details and fallback behavior

## API Reference

### loricaFetch(url, options, configuredUrls?)

Enhanced fetch function with automatic encryption.

**Parameters:**
- `url`: Request URL
- `options`: Standard fetch options
- `configuredUrls`: Optional list of known Lorica URLs

**Returns:** Promise<Response>

### Attestor Class

Main attestation handler with methods:
- `getOHTTPKeyConfig(url, attest)`: Get key configuration
- `getAttestationToken(url)`: Get JWT token
- `getAttestedDeploymentReport(url)`: Get full report
- `clearCache()`: Clear cached data

## Testing

Run tests with:
```bash
npm test src/lib/lorica
```

Test coverage includes:
- OHTTP encryption/decryption
- Attestation flow validation
- Error handling and fallbacks
- Cache management

## Dependencies

- `@hpke/core`: HPKE encryption implementation
- `jsonwebtoken`: JWT token parsing
- `crypto-js`: Cryptographic utilities
- `jwt-decode`: JWT payload extraction

## Future Enhancements

- Support for additional OHTTP suites
- Enhanced streaming response handling
- Performance optimizations
- Additional attestation providers
