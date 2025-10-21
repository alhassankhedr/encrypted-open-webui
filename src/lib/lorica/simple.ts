/**
 * Real Lorica integration with full encryption and attestation
 */

import { LoricaSession } from './session';
import { shouldUseLoricaEncryption } from './detector';
import { get } from 'svelte/store';
import { settings } from '$lib/stores';

// Global Lorica session instance
let loricaSession: LoricaSession | null = null;

function getLoricaSession(): LoricaSession {
	if (!loricaSession) {
		const currentSettings = get(settings);
		loricaSession = new LoricaSession({
			trusteeUrl: currentSettings.loricaTrusteeUrl || 'https://trustee.lorica.ai'
		});
		loricaSession.setConfiguredLoricaUrls(currentSettings.loricaBackendUrls || []);
	}
	return loricaSession;
}

export async function loricaFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
	const currentSettings = get(settings);
	const loricaEnabled = currentSettings.loricaEnabled || false;
	const loricaBackendUrls = currentSettings.loricaBackendUrls || [];

	const url = typeof input === 'string' ? input : input.toString();

	if (loricaEnabled && shouldUseLoricaEncryption(url, loricaBackendUrls)) {
		console.log(`🔒 Lorica fetch called (real implementation) for URL: ${url}`);
		const session = getLoricaSession();
		return await session.fetch(input, init);
	} else {
		console.log(`🌐 Standard fetch called for URL: ${url}`);
		return fetch(input, init);
	}
}

export function getLoricaConfig() {
	const currentSettings = get(settings);
	return {
		enabled: currentSettings.loricaEnabled || false,
		backendUrls: currentSettings.loricaBackendUrls || []
	};
}
