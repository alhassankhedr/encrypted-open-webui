/**
 * Lorica session wrapper for fetch API
 * Provides transparent encryption for requests to Lorica backends
 */

import { Attestor } from './attestor';
import { shouldUseLoricaEncryption } from './detector';
import { encapsulateRequest, decapsulateResponse, parseEncapsulatedRequest, createStreamingResponse } from './ohttp';
import { parseKeyConfig } from './ohttp';
import { OHTTPError, AttestationError } from './types';
import type { LoricaSessionOptions } from './types';

/**
 * Lorica session class that wraps fetch with encryption
 */
export class LoricaSession {
  private attestor: Attestor;
  private configuredLoricaUrls: string[];

  constructor(options: LoricaSessionOptions = {}) {
    this.attestor = new Attestor(options.trusteeUrl);
    this.configuredLoricaUrls = [];
  }

  /**
   * Set the list of configured Lorica backend URLs
   */
  setConfiguredLoricaUrls(urls: string[]): void {
    this.configuredLoricaUrls = urls;
  }

  /**
   * Enhanced fetch that automatically encrypts requests to Lorica backends
   */
  async fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    const request = new Request(input, init);
    const url = request.url;

    try {
      // Check if this URL should use Lorica encryption
      const useLorica = await shouldUseLoricaEncryption(url, this.configuredLoricaUrls);
      
      if (!useLorica) {
        // Use standard fetch for non-Lorica URLs
        return await window.fetch(input, init);
      }

      console.log(`[Lorica] Encrypting request to: ${url}`);

      // Get OHTTP key configuration and perform attestation
      const keyConfigBytes = await this.attestor.getOHTTPKeyConfig(url, true);
      const keyConfig = parseKeyConfig(keyConfigBytes);

      // Encapsulate the request
      const encapsulatedRequest = await encapsulateRequest(keyConfig, request);

      // Create the encrypted request
      const encryptedRequest = new Request(url, {
        method: 'POST', // OHTTP always uses POST
        headers: {
          'Content-Type': 'message/ohttp-req',
          'Content-Length': encapsulatedRequest.data.length.toString()
        },
        body: new Uint8Array(encapsulatedRequest.data)
      });

      // Send the encrypted request
      const response = await window.fetch(encryptedRequest);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Decapsulate the response
      const responseData = new Uint8Array(await response.arrayBuffer());
      const decryptedData = await decapsulateResponse(keyConfig, {
        data: responseData,
        keyId: encapsulatedRequest.keyId
      });

      // Check if this is a streaming response (for AI chat completions)
      const contentType = response.headers.get('content-type');
      const isStreaming = contentType?.includes('text/event-stream') || 
                         contentType?.includes('application/x-ndjson');

      if (isStreaming) {
      // Handle streaming response
      return this.handleStreamingResponse(new Uint8Array(decryptedData), response);
      } else {
        // Handle regular response
        return new Response(new Uint8Array(decryptedData), {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers
        });
      }

    } catch (error) {
      if (error instanceof AttestationError || error instanceof OHTTPError) {
        console.error(`[Lorica] Encryption failed for ${url}:`, error.message);
        // Fall back to unencrypted request
        console.warn(`[Lorica] Falling back to unencrypted request for ${url}`);
        return await window.fetch(input, init);
      }
      throw error;
    }
  }

  /**
   * Handle streaming responses (important for AI chat completions)
   */
  private handleStreamingResponse(decryptedData: Uint8Array, originalResponse: Response): Response {
    // For streaming responses, we need to create a new stream from the decrypted data
    const stream = new ReadableStream({
      start(controller) {
        // Process the decrypted data as a stream
        // This is a simplified implementation - in practice, you might need
        // to handle partial decryption for very large streams
        controller.enqueue(decryptedData);
        controller.close();
      }
    });

    return new Response(stream, {
      status: originalResponse.status,
      statusText: originalResponse.statusText,
      headers: originalResponse.headers
    });
  }

  /**
   * Get attestation token for a deployment
   */
  async getAttestationToken(url: string): Promise<string> {
    return await this.attestor.getAttestationToken(url);
  }

  /**
   * Get attested deployment report
   */
  async getAttestedDeploymentReport(url: string): Promise<any> {
    return await this.attestor.getAttestedDeploymentReport(url);
  }

  /**
   * Clear the attestation cache
   */
  clearCache(): void {
    this.attestor.clearCache();
  }
}

// Global Lorica session instance
let globalLoricaSession: LoricaSession | null = null;

/**
 * Get the global Lorica session instance
 */
export function getLoricaSession(): LoricaSession {
  if (!globalLoricaSession) {
    globalLoricaSession = new LoricaSession();
  }
  return globalLoricaSession;
}

/**
 * Enhanced fetch function that uses Lorica encryption when appropriate
 */
export async function loricaFetch(
  input: RequestInfo | URL, 
  init?: RequestInit,
  configuredLoricaUrls: string[] = []
): Promise<Response> {
  const session = getLoricaSession();
  session.setConfiguredLoricaUrls(configuredLoricaUrls);
  return await session.fetch(input, init);
}
