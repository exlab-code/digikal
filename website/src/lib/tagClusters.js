/**
 * Tag clustering helpers — single entry point used by both the SvelteKit site
 * and the D3 embed (via /tag-clusters.json endpoint). Edit tagClusters.json
 * to change grouping behavior; this module only derives lookups and provides
 * helper functions. Supports multiple dimensions (currently topic + audience).
 */
import data from './tagClusters.json';

export const TAG_CLUSTERS_DATA = data;

function buildDimension(dim) {
	const clusters = dim?.clusters || [];
	const drop = dim?.drop || [];
	const lowerDrop = new Set(drop.map((t) => t.toLowerCase()));
	const memberToCluster = new Map();
	for (const c of clusters) {
		for (const m of c.members) {
			memberToCluster.set(m.toLowerCase(), c.key);
		}
	}
	const keys = clusters.map((c) => c.key);
	const keySet = new Set(keys);
	return { clusters, drop, lowerDrop, memberToCluster, keys, keySet };
}

const TOPIC = buildDimension(data.topic);
const AUDIENCE = buildDimension(data.audience);

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
 * Normalize a raw tag to its cluster key within the given dimension.
 * Returns null for dropped (noise) tags, raw unchanged for unmapped.
 */
function clusterValue(dim, raw) {
	if (!raw) return null;
	const key = String(raw).toLowerCase().trim();
	if (dim.lowerDrop.has(key)) return null;
	return dim.memberToCluster.get(key) || raw;
}

function getDisplayValues(event, dim, groupKey) {
	const tg = parseTagGroups(event?.tag_groups);
	const raw = Array.isArray(tg[groupKey]) ? tg[groupKey] : [];
	const seen = new Set();
	const out = [];
	for (const t of raw) {
		const c = clusterValue(dim, t);
		if (!c || seen.has(c)) continue;
		seen.add(c);
		out.push(c);
	}
	return out;
}

function getOptions(events, dim, groupKey, minCountUnmapped) {
	const counts = new Map();
	for (const ev of events || []) {
		for (const key of getDisplayValues(ev, dim, groupKey)) {
			counts.set(key, (counts.get(key) || 0) + 1);
		}
	}
	return [...counts.entries()]
		.filter(([key, count]) => dim.keySet.has(key) || count >= minCountUnmapped)
		.map(([key, count]) => ({ key, count, isCluster: dim.keySet.has(key) }))
		.sort((a, b) => b.count - a.count || a.key.localeCompare(b.key));
}

// === Topic dimension ===
export const TOPIC_CLUSTER_KEYS = TOPIC.keys;
export const clusterTopic = (raw) => clusterValue(TOPIC, raw);
export const getDisplayTopics = (event) => getDisplayValues(event, TOPIC, 'topic');
export const getTopicOptions = (events, minCountUnmapped = 2) =>
	getOptions(events, TOPIC, 'topic', minCountUnmapped);
export const eventMatchesTopic = (event, selectedKey) => {
	if (!selectedKey) return true;
	return getDisplayTopics(event).includes(selectedKey);
};

// === Audience dimension ===
export const AUDIENCE_CLUSTER_KEYS = AUDIENCE.keys;
export const clusterAudience = (raw) => clusterValue(AUDIENCE, raw);
export const getDisplayAudience = (event) => getDisplayValues(event, AUDIENCE, 'audience');
export const getAudienceOptions = (events, minCountUnmapped = 2) =>
	getOptions(events, AUDIENCE, 'audience', minCountUnmapped);
export const eventMatchesAudience = (event, selectedKey) => {
	if (!selectedKey) return true;
	return getDisplayAudience(event).includes(selectedKey);
};

// === Back-compat aliases (topic was the only dimension before) ===
export const CLUSTERS = TOPIC.clusters;
export const DROP_TAGS = TOPIC.drop;
export const CLUSTER_KEYS = TOPIC.keys;
export const clusterTag = clusterTopic;
