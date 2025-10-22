<script lang="ts">
	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Cog6 from '$lib/components/icons/Cog6.svelte';
	import Lock from '$lib/components/icons/Lock.svelte';
	import CheckCircle from '$lib/components/icons/CheckCircle.svelte';
	import InfoCircle from '$lib/components/icons/InfoCircle.svelte';
	import AddLoricaConnectionModal from './AddLoricaConnectionModal.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	export let onDelete: () => void = () => {};
	export let onSubmit: (connection: any) => void = () => {};

	export let url = '';
	export let key = '';
	export let config: any = {};
	export let idx = 0;

	let showConfigModal = false;
	let showDeleteConfirmDialog = false;

	// Get attestation status from config
	$: attestation = config?.attestation;
	$: isAttestationVerified = attestation?.verified ?? false;
	$: trustLevel = attestation?.trust_level ?? 'unknown';
	$: hasAttestation = !!attestation;
</script>

<ConfirmDialog
	bind:show={showDeleteConfirmDialog}
	on:confirm={() => {
		onDelete();
	}}
/>

<AddLoricaConnectionModal
	edit
	bind:show={showConfigModal}
	connection={{
		url,
		key,
		config
	}}
	onDelete={() => {
		showDeleteConfirmDialog = true;
	}}
	onSubmit={(connection) => {
		url = connection.url;
		key = connection.key;
		config = connection.config;
		onSubmit(connection);
	}}
/>

<div class="flex w-full gap-2 items-center">
	<Tooltip
		className="w-full relative"
		content={$i18n.t(`WebUI will make requests to "{{url}}/v1/chat/completions" with OHTTP encryption`, {
			url
		})}
		placement="top-start"
	>
		{#if !(config?.enable ?? true)}
			<div
				class="absolute top-0 bottom-0 left-0 right-0 opacity-60 bg-white dark:bg-gray-900 z-10"
			></div>
		{/if}
		<div class="flex w-full gap-2">
			<div class="flex-1 relative">
				<input
					class="outline-hidden w-full bg-transparent pr-8"
					placeholder={$i18n.t('Lorica API Base URL')}
					bind:value={url}
					autocomplete="off"
					readonly={true}
				/>

				<!-- Attestation Status Indicator -->
				<div class="absolute top-0.5 right-2.5">
					{#if hasAttestation}
						{#if isAttestationVerified}
							<Tooltip content={$i18n.t('Attestation Verified - Trust Level: {{level}}', { level: trustLevel })}>
								<CheckCircle className="size-4 text-green-600 dark:text-green-400" />
							</Tooltip>
						{:else}
							<Tooltip content={$i18n.t('Attestation Failed - Connection may not be secure')}>
								<InfoCircle className="size-4 text-red-600 dark:text-red-400" />
							</Tooltip>
						{/if}
					{:else}
						<Tooltip content={$i18n.t('OHTTP Encrypted Connection - No attestation data')}>
							<Lock className="size-4 text-blue-600 dark:text-blue-400" />
						</Tooltip>
					{/if}
				</div>
			</div>
		</div>
	</Tooltip>

	<div class="flex gap-1">
		<Tooltip content={$i18n.t('Configure')} className="self-start">
			<button
				class="self-center p-1 bg-transparent hover:bg-gray-100 dark:bg-gray-900 dark:hover:bg-gray-850 rounded-lg transition"
				on:click={() => {
					showConfigModal = true;
				}}
				type="button"
			>
				<Cog6 />
			</button>
		</Tooltip>
	</div>
</div>

<!-- Attestation Details (if available) -->
{#if hasAttestation}
	<div class="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs">
		<div class="flex items-center gap-2 mb-1">
			{#if isAttestationVerified}
				<CheckCircle className="size-3 text-green-600 dark:text-green-400" />
				<span class="font-medium text-green-800 dark:text-green-200">
					{$i18n.t('Attestation Verified')}
				</span>
			{:else}
				<InfoCircle className="size-3 text-red-600 dark:text-red-400" />
				<span class="font-medium text-red-800 dark:text-red-200">
					{$i18n.t('Attestation Failed')}
				</span>
			{/if}
		</div>
		
		<div class="space-y-1 text-gray-600 dark:text-gray-400">
			{#if attestation.service_url}
				<div class="flex justify-between">
					<span>{$i18n.t('Service URL')}:</span>
					<span class="font-mono text-xs truncate max-w-32">{attestation.service_url}</span>
				</div>
			{/if}
			
			{#if attestation.trust_level}
				<div class="flex justify-between">
					<span>{$i18n.t('Trust Level')}:</span>
					<span class="font-medium">{attestation.trust_level}</span>
				</div>
			{/if}
			
			{#if attestation.timestamp}
				<div class="flex justify-between">
					<span>{$i18n.t('Verified At')}:</span>
					<span class="text-xs">{new Date(attestation.timestamp).toLocaleString()}</span>
				</div>
			{/if}
			
			{#if attestation.error}
					<div class="mt-1 p-1 bg-red-100 dark:bg-red-900/30 rounded text-xs">
					<span class="font-medium text-red-800 dark:text-red-200">{$i18n.t('Error')}:</span>
					<span class="text-red-700 dark:text-red-300">{attestation.error}</span>
				</div>
			{/if}
		</div>
	</div>
{/if}

<!-- Model IDs (if configured) -->
{#if config?.model_ids && config.model_ids.length > 0}
	<div class="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs">
		<div class="flex items-center gap-2 mb-1">
			<CheckCircle className="size-3 text-blue-600 dark:text-blue-400" />
			<span class="font-medium text-blue-800 dark:text-blue-200">
				{$i18n.t('Configured Models')} ({config.model_ids.length})
			</span>
		</div>
		<div class="flex flex-wrap gap-1">
			{#each config.model_ids as modelId}
				<span class="px-2 py-1 bg-blue-100 dark:bg-blue-800 rounded text-xs font-mono">
					{modelId}
				</span>
			{/each}
		</div>
	</div>
{/if}
