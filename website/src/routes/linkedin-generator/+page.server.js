import { getEvents } from '$lib/services/api.server.js';

export async function load() {
	const events = await getEvents();
	return { events };
}
