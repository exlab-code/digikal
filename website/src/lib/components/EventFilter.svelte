<script>
  import { onMount } from 'svelte';
  import { events, filters, updateFilters, availableMonths } from '$lib/stores/eventStore';
  import { getTopicOptions, getAudienceOptions } from '$lib/tagClusters.js';
  import Tag from './Tag.svelte';
  import Accordion from './Accordion.svelte';
  import { trackEvent } from '$lib/services/analytics';

  let selectedTags = [];
  let onlineOnly = false;
  let isFilterOpen = false; // Default closed on mobile
  let tagFrequency = {};
  let groupedTags = {
    "topic": [],
    "format": [],
    "audience": [],
    "cost": []
  };

  // Tag group names
  const tagGroupNames = {
    "topic": "Thema",
    "format": "Format",
    "audience": "Zielgruppe",
    "cost": "Kosten"
  };

  // Subscribe to the filters store to get current filter values
  filters.subscribe(f => {
    selectedTags = f.tags ? [...f.tags] : [];
    onlineOnly = f.onlineOnly || false;
  });

  // Initialize tag frequency and grouped tags on mount
  onMount(() => {
    calculateTagFrequency($events);
    groupedTags = getGroupedTags($events);
  });

  // Set minimum tag frequency
  const minTagFrequency = 3; // Only show tags that appear in at least 3 events

  // Update tag frequency based on future events only
  $: if ($events && $events.length > 0) {
    const futureEventsOnly = $events.filter(event => {
      if (!event.start_date) return false;
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const eventDate = new Date(event.start_date);
      const eventDay = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());
      return eventDay >= today;
    });

    tagFrequency = calculateTagFrequency(futureEventsOnly);
    groupedTags = getGroupedTags(futureEventsOnly);
  }
  
  function calculateTagFrequency(events) {
    const frequency = {};
    
    events.forEach(event => {
      if (event.tags && Array.isArray(event.tags)) {
        event.tags.forEach(tag => {
          frequency[tag] = (frequency[tag] || 0) + 1;
        });
      }
    });
    
    return frequency;
  }
  
  function getGroupedTags(events) {
    // Topic + audience use the central cluster map (cluster keys + long-tail ≥ minTagFrequency).
    const topicOptions = getTopicOptions(events, minTagFrequency);
    const audienceOptions = getAudienceOptions(events, minTagFrequency);
    // Overlay cluster counts onto tagFrequency so the Tag badge reflects cluster totals.
    topicOptions.forEach((o) => { tagFrequency[o.key] = o.count; });
    audienceOptions.forEach((o) => { tagFrequency[o.key] = o.count; });

    const groups = {
      "topic": topicOptions.map((o) => o.key),
      "format": new Set(),
      "audience": audienceOptions.map((o) => o.key),
      "cost": new Set()
    };

    // format / cost still come from raw tag_groups
    events.forEach(event => {
      if (event.tag_groups) {
        ['format', 'cost'].forEach((groupId) => {
          const tags = event.tag_groups[groupId] || [];
          tags.forEach(tag => {
            if (tagFrequency[tag] >= minTagFrequency) {
              groups[groupId].add(tag);
            }
          });
        });
      }
    });

    ['format', 'cost'].forEach((groupId) => {
      groups[groupId] = Array.from(groups[groupId]).sort();
    });

    return groups;
  }

  // Find the group ID for a tag
  function findTagGroup(tag) {
    for (const [groupId, tags] of Object.entries(groupedTags)) {
      if (tags.includes(tag)) {
        return groupId;
      }
    }
    return null;
  }

  function toggleTag(tag) {
    if (selectedTags.includes(tag)) {
      selectedTags = selectedTags.filter(t => t !== tag);
    } else {
      selectedTags = [...selectedTags, tag];
    }
    applyFilters();
    trackEvent('filter_change', { tags: selectedTags, onlineOnly });
  }

  function selectMonth(monthKey) {
    const newValue = $filters.selectedMonth === monthKey ? null : monthKey;
    updateFilters({ selectedMonth: newValue });
    trackEvent('filter_change', { selectedMonth: newValue });
  }

  function applyFilters() {
    updateFilters({
      tags: selectedTags,
      onlineOnly: onlineOnly
    });
  }

  function clearFilters() {
    selectedTags = [];
    onlineOnly = false;
    updateFilters({
      tags: [],
      onlineOnly: false,
      selectedMonth: null
    });
    trackEvent('filter_clear');
  }
</script>

<div class="bg-white rounded-lg shadow mb-6">
  <Accordion 
    title="Filter" 
    defaultOpen={true}
    mobileOnly={true}
    id="filter"
    on:toggle={({ detail }) => isFilterOpen = detail.isOpen}
  >
    <!-- Tag filters by group -->
    {#each Object.entries(groupedTags) as [groupId, tags]}
      {#if tags.length > 0}
        <div class="tag-group mb-4">
          <h3 class="tag-group-title">{tagGroupNames[groupId] || groupId}</h3>
          <div class="flex flex-wrap gap-1">
            {#each tags as tag}
              <Tag 
                {tag} 
                {groupId}
                selectable={true}
                selected={selectedTags.includes(tag)}
                count={tagFrequency[tag]}
                onClick={() => toggleTag(tag)}
              />
            {/each}
          </div>
        </div>
      {/if}
    {/each}
    
    <!-- Month filter -->
    {#if $availableMonths.length > 1}
      <div class="tag-group mb-4">
        <h3 class="tag-group-title">Monat</h3>
        <div class="flex flex-wrap gap-1.5">
          <button
            class="month-pill {$filters.selectedMonth === null ? 'selected' : ''}"
            on:click={() => selectMonth(null)}
          >
            Alle
          </button>
          {#each $availableMonths as month}
            <button
              class="month-pill {$filters.selectedMonth === month.key ? 'selected' : ''}"
              on:click={() => selectMonth(month.key)}
            >
              {month.label} <span class="month-pill-count">{month.count}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Filter Actions -->
    <div class="flex gap-1 flex-wrap">
      <button 
        type="button" 
        class="flex justify-center items-center px-4 py-2 border border-gray-300 text-sm rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        on:click={clearFilters}
        disabled={selectedTags.length === 0 && !onlineOnly && !$filters.selectedMonth}
      >
        <!-- <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg> -->
          Zurücksetzen
      </button>
    </div>
  </Accordion>
</div>
