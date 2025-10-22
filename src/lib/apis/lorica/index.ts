import { LORICA_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';

// Types for Lorica API responses
export type LoricaConfig = {
	enabled: boolean;
	base_urls: string[];
	api_keys: string[];
	configs: Record<string, any>;
};

export type LoricaAttestationResult = {
	verified: boolean;
	trust_level?: string;
	timestamp?: string;
	error?: string;
	service_url: string;
};

export type LoricaModel = {
	id: string;
	name: string;
	provider: string;
	context_length?: number;
	description?: string;
};

export type LoricaConnectionTestForm = {
	url: string;
	key: string;
};

export type LoricaChatCompletionRequest = {
	model: string;
	messages: Array<{ role: string; content: string }>;
	temperature?: number;
	max_tokens?: number;
	stream?: boolean;
};

// Health check
export const getLoricaHealth = async (token: string = '') => {
	let error = null;

	const res = await fetch(`${LORICA_API_BASE_URL}/health`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Configuration management
export const getLoricaConfig = async (token: string = ''): Promise<LoricaConfig> => {
	let error = null;

	const res = await fetch(`${LORICA_API_BASE_URL}/config`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateLoricaConfig = async (token: string = '', config: Partial<LoricaConfig>) => {
	let error = null;

	const res = await fetch(`${LORICA_API_BASE_URL}/config/update`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify({
			...config
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Connection verification and attestation
export const verifyLoricaConnection = async (
	token: string = '',
	urlIdx: number = 0
): Promise<LoricaAttestationResult> => {
	let error = null;

	const res = await fetch(`${LORICA_API_BASE_URL}/verify/${urlIdx}`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res.attestation;
};

export const testLoricaConnection = async (
	token: string = '',
	formData: LoricaConnectionTestForm
): Promise<LoricaAttestationResult> => {
	let error = null;

	const res = await fetch(`${LORICA_API_BASE_URL}/test_connection`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify(formData)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Models management
export const getLoricaModels = async (token: string = '', urlIdx: number = 0): Promise<LoricaModel[]> => {
	let error = null;

	const res = await fetch(`${LORICA_API_BASE_URL}/models/${urlIdx}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res.models || [];
};

// Chat completions
export const getLoricaChatCompletion = async (
	token: string = '',
	body: LoricaChatCompletionRequest,
	urlIdx: number = 0,
	url: string = `${WEBUI_BASE_URL}/api`
): Promise<[Response | null, AbortController]> => {
	const controller = new AbortController();
	let error = null;

	const res = await fetch(`${url}/lorica/chat/completions/${urlIdx}`, {
		signal: controller.signal,
		method: 'POST',
		headers: {
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(body)
	}).catch((err) => {
		console.error(err);
		error = err;
		return null;
	});

	if (error) {
		throw error;
	}

	return [res, controller];
};

export const generateLoricaChatCompletion = async (
	token: string = '',
	body: LoricaChatCompletionRequest,
	urlIdx: number = 0,
	url: string = `${WEBUI_BASE_URL}/api`
) => {
	let error = null;

	const res = await fetch(`${url}/lorica/chat/completions/${urlIdx}`, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		credentials: 'include',
		body: JSON.stringify(body)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err?.detail ?? err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

// Direct API calls (for testing connections)
export const getLoricaModelsDirect = async (url: string, key: string): Promise<LoricaModel[]> => {
	let error = null;

	const res = await fetch(`${url}/v1/models`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(key && { authorization: `Bearer ${key}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = `Lorica: ${err?.error?.message ?? 'Network Problem'}`;
			return { data: [] };
		});

	if (error) {
		throw error;
	}

	return res.data || [];
};

export const testLoricaConnectionDirect = async (
	url: string,
	key: string
): Promise<LoricaAttestationResult> => {
	let error = null;

	// Test with a simple models request
	const res = await fetch(`${url}/v1/models`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			Authorization: `Bearer ${key}`,
			'Content-Type': 'application/json'
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = `${err?.error?.message ?? 'Network Problem'}`;
			return null;
		});

	if (error) {
		throw error;
	}

	// Return a successful attestation result
	return {
		verified: true,
		trust_level: 'high',
		timestamp: new Date().toISOString(),
		service_url: url
	};
};
