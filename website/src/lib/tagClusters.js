/**
 * Tag clustering helpers — single entry point used by both the SvelteKit site
 * and the D3 embed (via /tag-clusters.json endpoint). Edit tagClusters.json
 * to change grouping behavior; this module only derives lookups and provides
 * helper functions.
 */
import data from './tagClusters.json';

export const TAG_CLUSTERS_DATA = data;
export const CLUSTERS = data.clusters;
export const DROP_TAGS = data.drop;

const LOWER_DROP = new Set(DROP_TAGS.map((t) => t.toLowerCase()));
const MEMBER_TO_CLUSTER = new Map();
for (const cluster of CLUSTERS) {
	for (const member of cluster.members) {
		MEMBER_TO_CLUSTER.set(member.toLowerCase(), cluster.key);
	}
}

export const CLUSTER_KEYS = CLUSTERS.map((c) => c.key);

/**
 * Normalize a single raw tag to its cluster key.
 * Returns null if the tag is in the drop list (pure noise).
 * Returns the raw tag unchanged if no cluster matches (preserves long-tail).
 */
export function clusterTag(raw) {
	if (!raw) return null;
	const key = String(raw).toLowerCase().trim();
	if (LOWER_DROP.has(key)) return null;
	return MEMBER_TO_CLUSTER.get(key) || raw;
}

/**
 * Parse tag_groups (object or JSON string), defaulting to {}.
 */
function parseTagGroups(tagGroups) {
	if (!tagGroups) return {};
	if (typeof tagGroups === 'string') {
		try {
			return JSON.parse(tagGroups);
		} catch {
			return {};
		}
	}
	return tagGroups;
}

/**
 * Return deduplicated display topics for an event: cluster keys for known
 * tags, raw strings for unmapped tags, with drop-list noise removed.
 */
export function getDisplayTopics(event) {
	const tg = parseTagGroups(event?.tag_groups);
	const raw = Array.isArray(tg.topic) ? tg.topic : [];
	const seen = new Set();
	const out = [];
	for (const t of raw) {
		const c = clusterTag(t);
		if (!c || seen.has(c)) continue;
		seen.add(c);
		out.push(c);
	}
	return out;
}

/**
 * Does this event match a selected topic key (cluster key or unmapped raw tag)?
 */
export function eventMatchesTopic(event, selectedKey) {
	if (!selectedKey) return true;
	return getDisplayTopics(event).includes(selectedKey);
}

/**
 * Return [{ key, count, isCluster }] sorted by count desc, then key asc.
 * `minCountUnmapped` hides long-tail unmapped tags below this frequency
 * (clusters are always shown).
 */
export function getTopicOptions(events, minCountUnmapped = 2) {
	const counts = new Map();
	for (const ev of events || []) {
		for (const key of getDisplayTopics(ev)) {
			counts.set(key, (counts.get(key) || 0) + 1);
		}
	}
	const clusterSet = new Set(CLUSTER_KEYS);
	return [...counts.entries()]
		.filter(([key, count]) => clusterSet.has(key) || count >= minCountUnmapped)
		.map(([key, count]) => ({ key, count, isCluster: clusterSet.has(key) }))
		.sort((a, b) => b.count - a.count || a.key.localeCompare(b.key));
}
