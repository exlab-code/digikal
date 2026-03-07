import { writable, derived } from 'svelte/store';

// Writable stores — populated from +page.server.js data
export const foerdermittel = writable([]);
export const filters = writable({
	searchQuery: '',
	tags: [],
	bundesland: '',
	fundingType: '',
	providerType: '',
	deadlineHorizon: 'all',
	fundingAmountRange: '',
	foerdergeber: '',
	source: ''
});
export const isLoading = writable(false);
export const error = writable(null);

function getDateRangeFromDeadlineHorizon(horizon) {
	const now = new Date();
	const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

	switch (horizon) {
		case 'thisMonth': {
			const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
			const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
			return { start: startOfMonth, end: endOfMonth };
		}
		case 'next3Months': {
			const end = new Date(today);
			end.setMonth(today.getMonth() + 3);
			return { start: today, end };
		}
		case 'next6Months': {
			const end = new Date(today);
			end.setMonth(today.getMonth() + 6);
			return { start: today, end };
		}
		case 'ongoing':
			return { type: 'ongoing' };
		case 'all':
		default:
			return { start: null, end: null };
	}
}

export const filteredFoerdermittel = derived(
	[foerdermittel, filters],
	([$foerdermittel, $filters]) => {
		const today = new Date();
		today.setHours(0, 0, 0, 0);

		return $foerdermittel.filter((program) => {
			// Search query
			if ($filters.searchQuery && $filters.searchQuery.trim() !== '') {
				const query = $filters.searchQuery.toLowerCase().trim();
				const searchableText = [
					program.title,
					program.original_title,
					program.description,
					program.funding_organization,
					program.eligibility_summary,
					program.funding_amount_text
				]
					.filter(Boolean)
					.join(' ')
					.toLowerCase();
				if (!searchableText.includes(query)) return false;
			}

			// Filter out past deadlines (keep laufend/jaehrlich)
			if (
				program.application_deadline &&
				program.deadline_type !== 'laufend' &&
				program.deadline_type !== 'jaehrlich'
			) {
				try {
					const deadlineDate = new Date(program.application_deadline);
					deadlineDate.setHours(0, 0, 0, 0);
					if (deadlineDate < today) return false;
				} catch (err) {
					/* ignore */
				}
			}

			// Tags (AND logic)
			if ($filters.tags && $filters.tags.length > 0) {
				if (!program.tag_groups) return false;
				const programTags = [];
				const tagGroupsObj =
					typeof program.tag_groups === 'string'
						? JSON.parse(program.tag_groups)
						: program.tag_groups;
				Object.values(tagGroupsObj).forEach((tags) => {
					if (Array.isArray(tags)) programTags.push(...tags.map((t) => t.toLowerCase()));
				});
				for (const filterTag of $filters.tags) {
					if (!programTags.includes(filterTag.toLowerCase())) return false;
				}
			}

			// Bundesland
			if ($filters.bundesland && $filters.bundesland !== '') {
				if (program.bundesland !== $filters.bundesland) return false;
			}

			// Funding type
			if ($filters.fundingType && $filters.fundingType !== '') {
				if (program.funding_type !== $filters.fundingType) return false;
			}

			// Provider type
			if ($filters.providerType && $filters.providerType !== '') {
				if (program.funding_provider_type !== $filters.providerType) return false;
			}

			// Deadline horizon
			if ($filters.deadlineHorizon && $filters.deadlineHorizon !== 'all') {
				const dateRange = getDateRangeFromDeadlineHorizon($filters.deadlineHorizon);
				if (dateRange.type === 'ongoing') {
					if (program.deadline_type !== 'laufend' && program.deadline_type !== 'jaehrlich')
						return false;
				} else if (dateRange.start || dateRange.end) {
					if (program.deadline_type === 'laufend' || program.deadline_type === 'jaehrlich')
						return false;
					if (program.application_deadline) {
						try {
							const deadlineDate = new Date(program.application_deadline);
							if (dateRange.start && deadlineDate < dateRange.start) return false;
							if (dateRange.end && deadlineDate > dateRange.end) return false;
						} catch (err) {
							/* ignore */
						}
					} else {
						return false;
					}
				}
			}

			// Funding amount range
			if ($filters.fundingAmountRange && $filters.fundingAmountRange !== '') {
				const min = program.funding_amount_min;
				const max = program.funding_amount_max;
				if (!min && !max) return true;
				const avgAmount = max ? (min + max) / 2 : min;
				switch ($filters.fundingAmountRange) {
					case 'small':
						if (avgAmount && avgAmount >= 10000) return false;
						break;
					case 'medium':
						if (!avgAmount || avgAmount < 10000 || avgAmount > 50000) return false;
						break;
					case 'large':
						if (!avgAmount || avgAmount < 50000 || avgAmount > 100000) return false;
						break;
					case 'xlarge':
						if (!avgAmount || avgAmount < 100000) return false;
						break;
				}
			}

			// Fördergeber
			if ($filters.foerdergeber && $filters.foerdergeber !== '') {
				if (program.funding_organization !== $filters.foerdergeber) return false;
			}

			// Source
			if ($filters.source && $filters.source !== '') {
				if (!program.source_url) return false;
				try {
					const domain = new URL(program.source_url).hostname;
					if (domain !== $filters.source) return false;
				} catch (e) {
					return false;
				}
			}

			return true;
		});
	}
);

export function updateFilters(newFilters) {
	filters.update((f) => ({ ...f, ...newFilters }));
}

export function resetFilters() {
	filters.set({
		searchQuery: '',
		tags: [],
		bundesland: '',
		fundingType: '',
		providerType: '',
		deadlineHorizon: 'all',
		fundingAmountRange: '',
		foerdergeber: '',
		source: ''
	});
}

export const topTags = derived(foerdermittel, ($foerdermittel) => {
	const tagCounts = {};
	for (const program of $foerdermittel) {
		if (program.tag_groups) {
			const tagGroupsObj =
				typeof program.tag_groups === 'string'
					? JSON.parse(program.tag_groups)
					: program.tag_groups;
			Object.values(tagGroupsObj).forEach((tags) => {
				if (Array.isArray(tags)) {
					for (const tag of tags) {
						tagCounts[tag] = (tagCounts[tag] || 0) + 1;
					}
				}
			});
		}
	}
	return Object.entries(tagCounts)
		.sort((a, b) => b[1] - a[1])
		.slice(0, 20)
		.map(([tag]) => tag);
});
