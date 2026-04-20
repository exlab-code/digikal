import { json } from '@sveltejs/kit';
import { TAG_CLUSTERS_DATA } from '$lib/tagClusters.js';

export const prerender = true;

export function GET() {
	return json(TAG_CLUSTERS_DATA, {
		headers: {
			'Cache-Control': 'public, max-age=3600',
			'Access-Control-Allow-Origin': '*'
		}
	});
}
