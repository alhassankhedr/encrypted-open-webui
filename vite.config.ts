import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
	plugins: [
		sveltekit(),
		viteStaticCopy({
			targets: [
				{
					src: 'node_modules/onnxruntime-web/dist/*.jsep.*',

					dest: 'wasm'
				}
			]
		})
	],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	build: {
		sourcemap: true
	},
	worker: {
		format: 'es'
	},
	esbuild: {
		pure: process.env.ENV === 'dev' ? [] : ['console.log', 'console.debug', 'console.error']
	},
	server: {
		proxy: {
			'/api/lorica/discover': {
				target: 'https://a1d90878.dep.lorica.ai',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api\/lorica/, ''),
				configure: (proxy, _options) => {
					proxy.on('error', (err, _req, _res) => {
						console.log('proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, _res) => {
						console.log('Sending Request to the Target:', req.method, req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, _res) => {
						console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
					});
				},
			},
			'/api/lorica/token': {
				target: 'https://a1d90878.dep.lorica.ai',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api\/lorica/, ''),
				configure: (proxy, _options) => {
					proxy.on('error', (err, _req, _res) => {
						console.log('proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, _res) => {
						console.log('Sending Request to the Target:', req.method, req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, _res) => {
						console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
					});
				},
			},
			'/api/lorica/trustee': {
				target: 'https://trustee.lorica.ai',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api\/lorica\/trustee/, ''),
				configure: (proxy, _options) => {
					proxy.on('error', (err, _req, _res) => {
						console.log('proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, _res) => {
						console.log('Sending Request to the Target:', req.method, req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, _res) => {
						console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
					});
				},
			},
			'/api': {
				target: 'http://localhost:3000',
				changeOrigin: true,
				configure: (proxy, _options) => {
					proxy.on('error', (err, _req, _res) => {
						console.log('Backend proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, _res) => {
						console.log('Backend Request:', req.method, req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, _res) => {
						console.log('Backend Response:', proxyRes.statusCode, req.url);
					});
				},
			}
		}
	}
});
