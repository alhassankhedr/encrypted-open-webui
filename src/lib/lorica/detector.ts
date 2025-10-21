/**
 * Lorica backend detection logic
 * Automatically detects if a URL belongs to a Lorica deployment
 */

import { OHTTPError } from './types';

/**
 * Cache for Lorica backend detection results
 */
class DetectionCache {
  private cache = new Map<string, { isLorica: boolean; timestamp: number }>();
  private ttl = 5 * 60 * 1000; // 5 minutes TTL

  set(url: string, isLorica: boolean): void {
    this.cache.set(url, {
      isLorica,
      timestamp: Date.now()
    });
  }

  get(url: string): boolean | null {
    const entry = this.cache.get(url);
    if (!entry) {
      return null;
    }

    const now = Date.now();
    if (now - entry.timestamp > this.ttl) {
      this.cache.delete(url);
      return null;
    }

    return entry.isLorica;
  }

  clear(): void {
    this.cache.clear();
  }
}

const detectionCache = new DetectionCache();

/**
 * Extract base URL from a full URL
 */
function getBaseUrl(url: string): string {
  try {
    const urlObj = new URL(url);
    return `${urlObj.protocol}//${urlObj.host}`;
  } catch (error) {
    throw new Error(`Invalid URL: ${url}`);
  }
}

/**
 * Check if a URL belongs to a Lorica deployment
 * Strategy: Try fetching the /discover endpoint to see if it returns valid OHTTP key config
 */
export async function isLoricaBackend(url: string): Promise<boolean> {
  const baseUrl = getBaseUrl(url);
  
  // Check cache first
  const cached = detectionCache.get(baseUrl);
  if (cached !== null) {
    return cached;
  }

  try {
    // Try to fetch the discover endpoint
    const discoverUrl = `${baseUrl}/discover`;
    const response = await fetch(discoverUrl, {
      method: 'GET',
      headers: {
        'Accept': 'text/plain'
      }
    });

    if (!response.ok) {
      detectionCache.set(baseUrl, false);
      return false;
    }

    // Check if response looks like a valid OHTTP key config
    const text = await response.text();
    const hexString = text.trim();
    
    // Basic validation: should be hex string with reasonable length
    if (!/^[0-9a-fA-F]+$/.test(hexString)) {
      detectionCache.set(baseUrl, false);
      return false;
    }

    // Convert to bytes and check minimum length
    const keyConfigBytes = new Uint8Array(Buffer.from(hexString, 'hex'));
    if (keyConfigBytes.length < 4) {
      detectionCache.set(baseUrl, false);
      return false;
    }

    // Additional validation: check if it looks like a valid OHTTP key config
    // First byte should be key ID (0-255)
    // Next 2 bytes should be suite ID
    // Third byte should be KEM ID
    const keyId = keyConfigBytes[0];
    const suiteId = (keyConfigBytes[1] << 8) | keyConfigBytes[2];
    const kemId = keyConfigBytes[3];

    // Basic sanity checks
    if (keyId > 255 || suiteId === 0 || kemId === 0) {
      detectionCache.set(baseUrl, false);
      return false;
    }

    // If we get here, it looks like a valid Lorica backend
    detectionCache.set(baseUrl, true);
    return true;

  } catch (error) {
    // Any error means it's not a Lorica backend
    detectionCache.set(baseUrl, false);
    return false;
  }
}

/**
 * Check if a URL should use Lorica encryption
 * This includes both automatic detection and explicit configuration
 */
export async function shouldUseLoricaEncryption(
  url: string, 
  configuredLoricaUrls: string[] = []
): Promise<boolean> {
  // First check if URL is explicitly configured as Lorica
  const baseUrl = getBaseUrl(url);
  if (configuredLoricaUrls.some(configuredUrl => getBaseUrl(configuredUrl) === baseUrl)) {
    return true;
  }

  // Otherwise, try automatic detection
  return await isLoricaBackend(url);
}

/**
 * Clear the detection cache
 */
export function clearDetectionCache(): void {
  detectionCache.clear();
}

/**
 * Get cache statistics for debugging
 */
export function getDetectionCacheStats(): { size: number; entries: string[] } {
  return {
    size: detectionCache['cache'].size,
    entries: Array.from(detectionCache['cache'].keys())
  };
}
