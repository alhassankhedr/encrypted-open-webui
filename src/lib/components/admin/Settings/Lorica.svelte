<!--
	Lorica encryption settings component
	Allows users to configure Lorica encryption for AI inference requests
-->
<script lang="ts">
	import { settings } from '$lib/stores';
	import { LORICA_DEFAULT_TRUSTEE_URL } from '$lib/constants';
	import { getLoricaSession } from '$lib/lorica';
	import { updateAdminConfig } from '$lib/apis/auths';
	import { onMount } from 'svelte';

	export let saveHandler: Function;

	let loricaEnabled = $settings.loricaEnabled || false;
	let trusteeUrl = $settings.loricaTrusteeUrl || LORICA_DEFAULT_TRUSTEE_URL;
	let attestationEnabled = $settings.loricaAttestationEnabled !== false; // default true
	let backendUrls = $settings.loricaBackendUrls || [];
	let newBackendUrl = '';
	let attestationStatus = '';
	let detailedLogs = '';
	let isCheckingAttestation = false;
	let showDetailedLogs = false;

	// Initialize settings on mount
	onMount(() => {
		console.log('Lorica component mounted, settings:', $settings);
		console.log('Lorica settings from store:', {
			loricaEnabled: $settings.loricaEnabled,
			loricaTrusteeUrl: $settings.loricaTrusteeUrl,
			loricaAttestationEnabled: $settings.loricaAttestationEnabled,
			loricaBackendUrls: $settings.loricaBackendUrls
		});
		
		// Load settings from store (which comes from backend config)
		console.log('Loading Lorica settings from store:', {
			loricaEnabled: $settings.loricaEnabled,
			loricaTrusteeUrl: $settings.loricaTrusteeUrl,
			loricaAttestationEnabled: $settings.loricaAttestationEnabled,
			loricaBackendUrls: $settings.loricaBackendUrls
		});
		
		loricaEnabled = $settings.loricaEnabled || false;
		trusteeUrl = $settings.loricaTrusteeUrl || LORICA_DEFAULT_TRUSTEE_URL;
		attestationEnabled = $settings.loricaAttestationEnabled !== false;
		backendUrls = $settings.loricaBackendUrls || [];
		
		console.log('Lorica component initialized with:', {
			loricaEnabled,
			trusteeUrl,
			attestationEnabled,
			backendUrls
		});
	});

	async function updateSettings() {
		console.log('Updating Lorica settings:', { loricaEnabled, trusteeUrl, attestationEnabled, backendUrls });
		
		// Update local settings store
		settings.update((s) => ({
			...s,
			loricaEnabled,
			loricaBackendUrls: backendUrls
		}));
		
		// Save to backend
		try {
			const token = localStorage.getItem('token');
			if (token) {
				await updateAdminConfig(token, {
					loricaEnabled,
					loricaBackendUrls: backendUrls
				});
				console.log('Lorica settings saved to backend');
			}
		} catch (error) {
			console.error('Failed to save Lorica settings:', error);
		}
		
		// Settings are now persisted to backend database
		
		// Call the save handler to show success message
		if (saveHandler) {
			console.log('Calling saveHandler');
			saveHandler();
		}
	}

	function addBackendUrl() {
		if (newBackendUrl.trim() && !backendUrls.includes(newBackendUrl.trim())) {
			backendUrls = [...backendUrls, newBackendUrl.trim()];
			newBackendUrl = '';
			// Don't auto-save when adding URLs, let user save manually
		}
	}

	function removeBackendUrl(url: string) {
		backendUrls = backendUrls.filter((u) => u !== url);
		// Don't auto-save when removing URLs, let user save manually
	}

	async function checkAttestation() {
		console.log('🔐 checkAttestation called');
		attestationStatus = 'Starting attestation check...';
		
		if (!backendUrls.length) {
			attestationStatus = 'No backend URLs configured';
			return;
		}

		isCheckingAttestation = true;
		attestationStatus = 'Checking attestation...';

		try {
			const session = getLoricaSession();
			const results = [];
			const logs = [];

			for (const url of backendUrls) {
				try {
					console.log(`🔍 Testing connectivity to: ${url}`);
					logs.push(`🔍 Testing connectivity to: ${url}`);
					
					// First, test basic connectivity via Vite proxy
					const proxyUrl = `/api/lorica/discover`;
					console.log(`📡 Making request to Vite proxy: ${proxyUrl}`);
					logs.push(`📡 Making request to Vite proxy: ${proxyUrl}`);
					
					const response = await fetch(proxyUrl, { 
						method: 'GET',
						credentials: 'include'
					});
					
					console.log(`📊 Response status: ${response.status} ${response.statusText}`);
					console.log(`📊 Response headers:`, Object.fromEntries(response.headers.entries()));
					logs.push(`📊 Response status: ${response.status} ${response.statusText}`);
					logs.push(`📊 Response headers: ${JSON.stringify(Object.fromEntries(response.headers.entries()))}`);
					
					if (!response.ok) {
						results.push(`❌ ${url}: Not a Lorica deployment (${response.status})`);
						continue;
					}

					// Check if we got OHTTP key config data
					const contentType = response.headers.get('content-type');
					const contentLength = response.headers.get('content-length');
					
					console.log(`📊 Content-Type: ${contentType}, Content-Length: ${contentLength}`);
					logs.push(`📊 Content-Type: ${contentType}, Content-Length: ${contentLength}`);
					
					if (!contentLength || parseInt(contentLength) < 50) {
						results.push(`❌ ${url}: Invalid OHTTP key config (too short)`);
						continue;
					}

					console.log(`✅ Basic connectivity test passed for ${url}`);
					logs.push(`✅ Basic connectivity test passed for ${url}`);
					
					// Try to get attestation report
					console.log(`🔐 Starting attestation process for ${url}`);
					logs.push(`🔐 Starting attestation process for ${url}`);
					const report = await session.getAttestedDeploymentReport(url);
					results.push(`✅ ${url}: Attestation successful`);
					logs.push(`✅ ${url}: Attestation successful`);
				} catch (error) {
					const errorMessage = error instanceof Error ? error.message : String(error);
					console.log(`❌ Attestation error for ${url}:`, error);
					console.log(`❌ Error type:`, error instanceof Error ? error.constructor.name : 'Unknown');
					console.log(`❌ Error stack:`, error instanceof Error ? error.stack : 'No stack');
					logs.push(`❌ Attestation error for ${url}: ${errorMessage}`);
					logs.push(`❌ Error type: ${error instanceof Error ? error.constructor.name : 'Unknown'}`);
					
					if (errorMessage.includes('Failed to fetch key config')) {
						results.push(`❌ ${url}: OHTTP key config fetch failed`);
					} else if (errorMessage.includes('Failed to fetch')) {
						results.push(`❌ ${url}: Network error - check connectivity`);
					} else if (errorMessage.includes('OHTTP key config fetch failed')) {
						results.push(`❌ ${url}: Lorica backend error - check deployment status`);
					} else if (errorMessage.includes('AttestationError')) {
						results.push(`❌ ${url}: Attestation failed - ${errorMessage}`);
					} else if (errorMessage.includes('JWT')) {
						results.push(`❌ ${url}: JWT validation failed - ${errorMessage}`);
					} else if (errorMessage.includes('Trustee')) {
						results.push(`❌ ${url}: Trustee service error - ${errorMessage}`);
					} else {
						results.push(`❌ ${url}: ${errorMessage}`);
					}
				}
			}

			// Show basic results first
			attestationStatus = results.join('\n');
			// Store detailed logs separately
			detailedLogs = logs.filter(log => log.trim()).join('\n');
		} catch (error) {
			console.log(`❌ Overall attestation error:`, error);
			attestationStatus = `Error checking attestation: ${error instanceof Error ? error.message : String(error)}`;
		} finally {
			isCheckingAttestation = false;
		}
	}

	function clearCache() {
		console.log('🗑️ clearCache called');
		const session = getLoricaSession();
		session.clearCache();
		attestationStatus = 'Cache cleared';
	}

	async function testBasicConnectivity() {
		console.log('🧪 testBasicConnectivity called');
		attestationStatus = 'Testing connectivity...';
		
		try {
			// Test a simple request to see if CORS is the issue
			const testUrl = 'https://httpbin.org/get';
			console.log(`📡 Testing with httpbin.org: ${testUrl}`);
			
			const response = await fetch(testUrl, {
				method: 'GET',
				mode: 'cors',
				credentials: 'omit'
			});
			
			console.log(`✅ httpbin.org test: ${response.status} ${response.statusText}`);
			
			// Now test the Lorica backend through Vite proxy
			const loricaProxyUrl = '/api/lorica/discover';
			console.log(`📡 Testing Lorica backend via Vite proxy: ${loricaProxyUrl}`);
			
			const loricaResponse = await fetch(loricaProxyUrl, {
				method: 'GET',
				credentials: 'include'
			});
			
			console.log(`📊 Lorica proxy response: ${loricaResponse.status} ${loricaResponse.statusText}`);
			console.log(`📊 Lorica proxy headers:`, Object.fromEntries(loricaResponse.headers.entries()));
			
			if (loricaResponse.ok) {
				const data = await loricaResponse.arrayBuffer();
				console.log(`📊 Lorica data length: ${data.byteLength} bytes`);
				attestationStatus = `✅ Connectivity test successful!\n- httpbin.org: ${response.status} OK\n- Lorica backend (via proxy): ${loricaResponse.status} OK (${data.byteLength} bytes)`;
			} else {
				attestationStatus = `❌ Lorica backend test failed: ${loricaResponse.status} ${loricaResponse.statusText}`;
			}
			
		} catch (error) {
			console.log(`❌ Basic connectivity test failed:`, error);
			attestationStatus = `❌ Connectivity test failed: ${error instanceof Error ? error.message : String(error)}`;
		}
	}

	onMount(() => {
		console.log('Lorica component mounted, initial settings:', {
			loricaEnabled: $settings.loricaEnabled,
			trusteeUrl: $settings.loricaTrusteeUrl,
			attestationEnabled: $settings.loricaAttestationEnabled,
			backendUrls: $settings.loricaBackendUrls
		});
		
		// Add example backend URLs if none exist
		if (backendUrls.length === 0) {
			backendUrls = [
				'https://a1d90878.dep.lorica.ai', // Your existing Lorica backend
				'https://trustee.lorica.ai' // Trustee service for testing
			];
			updateSettings();
		}
		
		// Test if functions are working
		console.log('Testing function availability:');
		console.log('checkAttestation:', typeof checkAttestation);
		console.log('testBasicConnectivity:', typeof testBasicConnectivity);
		console.log('clearCache:', typeof clearCache);
		console.log('getLoricaSession:', typeof getLoricaSession);
	});
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
				Lorica Encryption
			</h3>
			<p class="text-sm text-gray-500 dark:text-gray-400">
				Enable encrypted AI inference requests using Lorica's OHTTP protocol with attestation
			</p>
		</div>
		<label class="relative inline-flex items-center cursor-pointer">
			<input
				type="checkbox"
				bind:checked={loricaEnabled}
				on:change={() => {
					console.log('Toggle changed, loricaEnabled is now:', loricaEnabled);
					updateSettings();
				}}
				class="sr-only peer"
			/>
			<div
				class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
			></div>
		</label>
	</div>

	{#if loricaEnabled}
		<div class="space-y-4">
			<!-- Trustee URL Configuration -->
			<div>
				<label for="trustee-url" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
					Trustee URL
				</label>
				<input
					id="trustee-url"
					type="url"
					bind:value={trusteeUrl}
					on:change={updateSettings}
					placeholder="https://trustee.lorica.ai"
					class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
				/>
				<p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
					The Trustee service URL for attestation validation
				</p>
			</div>

			<!-- Attestation Toggle -->
			<div class="flex items-center justify-between">
				<div>
					<label class="text-sm font-medium text-gray-700 dark:text-gray-300">
						Enable Attestation
					</label>
					<p class="text-xs text-gray-500 dark:text-gray-400">
						Perform JWT validation and PCR checks for enhanced security
					</p>
				</div>
				<label class="relative inline-flex items-center cursor-pointer">
					<input
						type="checkbox"
						bind:checked={attestationEnabled}
						on:change={updateSettings}
						class="sr-only peer"
					/>
					<div
						class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"
					></div>
				</label>
			</div>

			<!-- Backend URLs Management -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Lorica Backend URLs
				</label>
				<div class="space-y-2">
					<!-- Add new URL -->
					<div class="flex gap-2">
						<input
							type="url"
							bind:value={newBackendUrl}
							placeholder="https://your-lorica-backend.com"
							class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
							on:keydown={(e) => e.key === 'Enter' && addBackendUrl()}
						/>
						<button
							type="button"
							on:click={addBackendUrl}
							disabled={!newBackendUrl.trim()}
							class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Add
						</button>
					</div>

					<!-- List of configured URLs -->
					{#if backendUrls.length > 0}
						<div class="space-y-1">
							{#each backendUrls as url}
								<div class="flex items-center justify-between bg-gray-50 dark:bg-gray-800 px-3 py-2 rounded-md">
									<span class="text-sm text-gray-700 dark:text-gray-300 font-mono">{url}</span>
									<button
										type="button"
										on:click={() => removeBackendUrl(url)}
										class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
									>
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
										</svg>
									</button>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-gray-500 dark:text-gray-400 italic">
							No backend URLs configured. URLs will be auto-detected by probing the /discover endpoint.
						</p>
					{/if}
				</div>
			</div>

			<!-- Attestation Status and Actions -->
			<div class="border-t border-gray-200 dark:border-gray-700 pt-4">
				<div class="flex items-center justify-between mb-2">
					<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300">
						Attestation Status
					</h4>
					<div class="flex gap-2">
						<button
							type="button"
							on:click={checkAttestation}
							disabled={isCheckingAttestation}
							class="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
						>
							{isCheckingAttestation ? 'Checking...' : 'Check Status'}
						</button>
						<button
							type="button"
							on:click={clearCache}
							class="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
						>
							Clear Cache
						</button>
						<button
							type="button"
							on:click={testBasicConnectivity}
							class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
						>
							Test Connectivity
						</button>
						<button
							type="button"
							on:click={() => showDetailedLogs = !showDetailedLogs}
							class="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700"
						>
							{showDetailedLogs ? 'Hide' : 'Show'} Detailed Logs
						</button>
					</div>
				</div>
				
				{#if attestationStatus}
					<pre class="text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded-md overflow-auto max-h-32 text-gray-700 dark:text-gray-300">{#if showDetailedLogs && detailedLogs}
{attestationStatus.trim()}

--- Detailed Logs ---
{detailedLogs}
{:else}
{attestationStatus.trim()}
{/if}</pre>
				{/if}
			</div>

			<!-- Information Panel -->
			<div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-4">
				<div class="flex">
					<div class="flex-shrink-0">
						<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
						</svg>
					</div>
					<div class="ml-3">
						<h3 class="text-sm font-medium text-blue-800 dark:text-blue-200">
							Lorica Encryption Information
						</h3>
						<div class="mt-2 text-sm text-blue-700 dark:text-blue-300">
							<p>
								When enabled, all AI inference requests to Lorica backends will be automatically encrypted using the OHTTP protocol.
								This provides end-to-end encryption and attestation for enhanced security and privacy.
							</p>
							<ul class="mt-2 list-disc list-inside space-y-1">
								<li>Requests are encrypted using Hybrid Public Key Encryption (HPKE)</li>
								<li>Attestation verifies the integrity of the backend deployment</li>
								<li>PCR checks ensure the OHTTP key matches the attested enclave</li>
								<li>Automatic fallback to unencrypted requests if encryption fails</li>
							</ul>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
