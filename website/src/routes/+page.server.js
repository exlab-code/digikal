import { getEvents, getCalendarUrls } from '$lib/services/api.server.js';

export async function load() {
	const [events, calendarUrls] = await Promise.all([getEvents(), getCalendarUrls()]);

	return { events, calendarUrls };
}
