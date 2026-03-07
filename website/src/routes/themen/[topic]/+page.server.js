import { error } from '@sveltejs/kit';
import { TOPICS } from '$lib/topics.js';
import { getEvents } from '$lib/services/api.server.js';
import { readFileSync } from 'fs';
import { resolve } from 'path';

export const prerender = true;

export function entries() {
	return Object.keys(TOPICS).map((topic) => ({ topic }));
}

export async function load({ params }) {
	const topicConfig = TOPICS[params.topic];
	if (!topicConfig) {
		throw error(404, 'Thema nicht gefunden');
	}

	// Fetch events
	let allEvents = [];
	try {
		allEvents = await getEvents();
	} catch (err) {
		console.error('Failed to fetch events for topic page:', err);
	}

	// Filter events matching this topic
	const now = new Date();
	const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

	const events = allEvents
		.filter((event) => {
			if (!event.start_date) return false;
			const eventDate = new Date(event.start_date);
			if (new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate()) < today)
				return false;
			if (!event.tags && !event.tag_groups) return false;

			// Check flat tags
			const eventTags = (event.tags || []).map((t) => t.toLowerCase());
			const flatMatch = topicConfig.eventTags.some((tag) =>
				eventTags.some((et) => et.includes(tag.toLowerCase()))
			);
			if (flatMatch) return true;

			// Check tag_groups (e.g. tag_groups.topic)
			if (event.tag_groups) {
				const tg = typeof event.tag_groups === 'string' ? JSON.parse(event.tag_groups) : event.tag_groups;
				const allGroupTags = Object.values(tg).flat().map((t) => t.toLowerCase());
				return topicConfig.eventTags.some((tag) =>
					allGroupTags.some((gt) => gt.includes(tag.toLowerCase()))
				);
			}
			return false;
		})
		.slice(0, 20);

	// Load Fördermittel from static JSON
	let allFoerdermittel = [];
	try {
		const jsonPath = resolve('static', 'foerdermittel.json');
		const raw = readFileSync(jsonPath, 'utf-8');
		allFoerdermittel = JSON.parse(raw);
	} catch (err) {
		console.error('Failed to load foerdermittel.json for topic page:', err);
	}

	const foerdermittel = allFoerdermittel
		.filter((program) => {
			// Filter out past deadlines
			if (
				program.application_deadline &&
				program.deadline_type !== 'laufend' &&
				program.deadline_type !== 'jaehrlich'
			) {
				const deadline = new Date(program.application_deadline);
				if (deadline < today) return false;
			}

			if (!program.tag_groups) return false;
			const tagGroupsObj =
				typeof program.tag_groups === 'string'
					? JSON.parse(program.tag_groups)
					: program.tag_groups;
			const allTags = Object.values(tagGroupsObj)
				.flat()
				.map((t) => t.toLowerCase());
			return topicConfig.foerdermittelTags.some((tag) =>
				allTags.some((pt) => pt.includes(tag.toLowerCase()))
			);
		})
		.slice(0, 10);

	return {
		topic: params.topic,
		topicConfig,
		events,
		foerdermittel
	};
}
