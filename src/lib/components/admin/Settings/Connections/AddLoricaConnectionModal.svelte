<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	import Modal from '$lib/components/common/Modal.svelte';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import CheckCircle from '$lib/components/icons/CheckCircle.svelte';
	import InfoCircle from '$lib/components/icons/InfoCircle.svelte';
	import Lock from '$lib/components/icons/Lock.svelte';

	import { 
		testLoricaConnectionDirect,
		type LoricaAttestationResult
	} from '$lib/apis/lorica';

	export let onSubmit: (connection: any) => void = () => {};
	export let onDelete: () => void = () => {};

	export let show = false;
	export let edit = false;
	export let connection: any = null;

	let url = '';
	let key = '';
	let tags: string[] = [];
	let modelId = '';
	let modelIds: string[] = [];

	let loading = false;
	let verifying = false;
	let attestationResult: LoricaAttestationResult | null = null;
	let showAttestation = false;

	const verifyLoricaConnection = async () => {
		if (!url || !key || !modelId) {
			toast.error($i18n.t('URL, API Key, and Model ID are required'));
			return;
		}

		verifying = true;
		attestationResult = null;

		try {
			// Test connection and get attestation
			const attestation = await testLoricaConnectionDirect(url, key, modelId);
			attestationResult = attestation;
			showAttestation = true;

			if (attestation.verified) {
				toast.success($i18n.t('Lorica connection verified with attestation'));
			} else {
				toast.warning($i18n.t('Connection successful but attestation failed'));
			}
		} catch (error) {
			console.error('Lorica connection test failed:', error);
			toast.error(`${$i18n.t('Lorica')}: ${error}`);
			attestationResult = {
				verified: false,
				error: String(error),
				service_url: url
			};
			showAttestation = true;
		} finally {
			verifying = false;
		}
	};

	const addModelHandler = () => {
		if (modelId && !modelIds.includes(modelId)) {
			modelIds = [...modelIds, modelId];
			modelId = '';
		}
	};

	const removeModelHandler = (index: number) => {
		modelIds = modelIds.filter((_, i) => i !== index);
	};

	const submitHandler = async () => {
		loading = true;

		if (!url) {
			loading = false;
			toast.error($i18n.t('URL is required'));
			return;
		}

		if (!key) {
			loading = false;
			toast.error($i18n.t('API Key is required'));
			return;
		}

		// remove trailing slash from url
		url = url.replace(/\/$/, '');

		const loricaConnection = {
			url,
			key,
			modelId,
			config: {
				modelId: modelId,
				tags: tags,
				model_ids: modelIds,
				attestation: attestationResult
			}
		};

		await onSubmit(loricaConnection);

		loading = false;
		show = false;

		// Only reset form when adding a new connection, not when editing
		if (!edit) {
			// Reset form
			url = '';
			key = '';
			modelId = '';
			tags = [];
			modelIds = [];
			attestationResult = null;
			showAttestation = false;
		}
	};

	const init = () => {
		if (connection) {
			url = connection.url;
			key = connection.key;
			modelId = connection.modelId ?? '';
			tags = connection.config?.tags ?? [];
			modelIds = connection.config?.model_ids ?? [];
			attestationResult = connection.config?.attestation ?? null;
			showAttestation = !!attestationResult;
		}
	};

	$: if (show) {
		init();
	}

</script>

<Modal size="lg" bind:show>
	<div>
		<div class="flex justify-between dark:text-gray-100 px-5 pt-4 pb-1.5">
			<h1 class="text-lg font-medium self-center font-primary">
				{#if edit}
					{$i18n.t('Edit Lorica Connection')}
				{:else}
					{$i18n.t('Add Lorica Connection')}
				{/if}
			</h1>
			<button
				class="self-center"
				aria-label={$i18n.t('Close modal')}
				on:click={() => {
					show = false;
				}}
			>
				<XMark className={'size-5'} />
			</button>
		</div>

		<div class="flex flex-col w-full px-4 pb-4 dark:text-gray-200">
			<form
				class="flex flex-col w-full"
				on:submit={(e) => {
					e.preventDefault();
					submitHandler();
				}}
			>
				<div class="px-1 space-y-4">
					<!-- URL Input -->
					<div class="flex flex-col w-full">
						<label
							for="lorica-url-input"
							class="mb-0.5 text-xs text-gray-500"
						>
							{$i18n.t('Lorica API Base URL')}
						</label>
						<input
							id="lorica-url-input"
							class="w-full bg-transparent outline-hidden"
							placeholder="https://your-lorica-endpoint.ai"
							bind:value={url}
							autocomplete="off"
							required
						/>
					</div>

					<!-- API Key Input -->
					<div class="flex flex-col w-full">
						<label
							for="lorica-key-input"
							class="mb-0.5 text-xs text-gray-500"
						>
							{$i18n.t('API Key')}
						</label>
						<SensitiveInput
							id="lorica-key-input"
							outerClassName="w-full"
							inputClassName="w-full bg-transparent outline-hidden"
							placeholder="Your Lorica API key"
							bind:value={key}
							required
						/>
					</div>

					<!-- Model ID Input -->
					<div class="flex flex-col w-full">
						<label
							for="lorica-model-input"
							class="mb-0.5 text-xs text-gray-500"
						>
							{$i18n.t('Model ID')} <span class="text-red-500">*</span>
						</label>
						<input
							id="lorica-model-input"
							class="w-full bg-transparent outline-hidden border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm"
							placeholder="cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic"
							bind:value={modelId}
							required
						/>
						<div class="mt-1 text-xs text-gray-500">
							{$i18n.t('Enter the model ID for this Lorica connection')}
						</div>
					</div>

					<!-- Connection Test Button -->
					<div class="flex flex-col w-full">
						<button
							type="button"
							class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition flex items-center justify-center gap-2"
							on:click={verifyLoricaConnection}
							disabled={verifying || !url || !key || !modelId}
						>
							{#if verifying}
								<Spinner className="size-4" />
								{$i18n.t('Verifying Connection...')}
							{:else}
								<Lock className="size-4" />
								{$i18n.t('Test Connection & Attestation')}
							{/if}
						</button>
					</div>

					<!-- Attestation Results -->
					{#if showAttestation && attestationResult}
						<div class="border rounded-lg p-4 {attestationResult.verified ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20' : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'}">
							<div class="flex items-center gap-2 mb-2">
								{#if attestationResult.verified}
									<CheckCircle className="size-5 text-green-600 dark:text-green-400" />
									<span class="font-medium text-green-800 dark:text-green-200">
										{$i18n.t('Attestation Verified')}
									</span>
								{:else}
									<InfoCircle className="size-5 text-red-600 dark:text-red-400" />
									<span class="font-medium text-red-800 dark:text-red-200">
										{$i18n.t('Attestation Failed')}
									</span>
								{/if}
							</div>
							
							<div class="text-sm space-y-1">
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">{$i18n.t('Service URL')}:</span>
									<span class="font-mono text-xs">{attestationResult.service_url}</span>
								</div>
								
								{#if attestationResult.trust_level}
									<div class="flex justify-between">
										<span class="text-gray-600 dark:text-gray-400">{$i18n.t('Trust Level')}:</span>
										<span class="font-medium">{attestationResult.trust_level}</span>
									</div>
								{/if}
								
								{#if attestationResult.timestamp}
									<div class="flex justify-between">
										<span class="text-gray-600 dark:text-gray-400">{$i18n.t('Verified At')}:</span>
										<span class="text-xs">{new Date(attestationResult.timestamp).toLocaleString()}</span>
									</div>
								{/if}
								
								{#if attestationResult.error}
									<div class="mt-2 p-2 bg-red-100 dark:bg-red-900/30 rounded text-xs">
										<span class="font-medium text-red-800 dark:text-red-200">{$i18n.t('Error')}:</span>
										<span class="text-red-700 dark:text-red-300">{attestationResult.error}</span>
									</div>
								{/if}
							</div>
						</div>
					{/if}



				</div>

				<!-- Submit Button -->
				<div class="flex justify-end gap-2 mt-6">
					{#if edit && onDelete}
						<button
							type="button"
							class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
							on:click={() => onDelete()}
						>
							{$i18n.t('Delete')}
						</button>
					{/if}
					
					<button
						type="button"
						class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition"
						on:click={() => {
							show = false;
						}}
					>
						{$i18n.t('Cancel')}
					</button>
					
					<button
						type="submit"
						class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition flex items-center gap-2"
						disabled={loading || !url || !key || !modelId}
					>
						{#if loading}
							<Spinner className="size-4" />
						{/if}
						{$i18n.t('Save Connection')}
					</button>
				</div>
			</form>
		</div>
	</div>
</Modal>
