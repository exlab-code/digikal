import { error } from '@sveltejs/kit';
import { getEvents } from '$lib/services/api.server.js';
import { slugify, eventPath, findSimilarEvents } from '$lib/eventHelpers.js';

export const prerender = true;

/**
 * Generate one entry per approved event.
 * The slug is `{id}-{titleSlug}` so titles can collide safely.
 */
export async function entries() {
	const events = await getEvents();
	return events.map((event) => ({
		slug: `${event.id}-${slugify(event.title)}`
	}));
}

/**
 * Look up the event by parsing the leading numeric id from the slug.
 * @param {{ params: { slug: string } }} args
 */
export async function load({ params }) {
	const match = params.slug.match(/^(\d+)(?:-.*)?$/);
	if (!match) throw error(404, 'Veranstaltung nicht gefunden');

	const id = match[1];
	const events = await getEvents();
	const event = events.find((e) => String(e.id) === id);
	if (!event) throw error(404, 'Veranstaltung nicht gefunden');

	const canonicalSlug = `${event.id}-${slugify(event.title)}`;
	const similar = findSimilarEvents(event, events, 5);

	return {
		event,
		canonicalSlug,
		canonicalPath: eventPath(event),
		similar
	};
}
