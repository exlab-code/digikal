<script>
  import { getCategoryName } from '$lib/categoryMappings';
  import Tag from './Tag.svelte';
  import { filters, updateFilters } from '$lib/stores/eventStore';

  export let event;

  // Extract time (HH:MM) from an ISO datetime string, returns null for date-only or midnight
  function extractTime(dateString) {
    if (!dateString || !dateString.includes('T')) return null;
    const d = new Date(dateString);
    const h = d.getHours(), m = d.getMinutes();
    if (h === 0 && m === 0) return null;
    return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}`;
  }


  $: startTime = extractTime(event.start_date);
  $: endTime = extractTime(event.end_date);
  $: link = event.website || event.register_link;

  // Find the group ID for a tag
  function findTagGroup(tag) {
    if (!event.tag_groups) return null;
    for (const [groupId, tags] of Object.entries(event.tag_groups)) {
      if (tags.includes(tag)) return groupId;
    }
    return null;
  }

  function toggleTag(tag, e) {
    e.preventDefault();
    e.stopPropagation();
    const current = $filters.tags || [];
    const updated = current.includes(tag)
      ? current.filter(t => t !== tag)
      : [...current, tag];
    updateFilters({ tags: updated });
  }


</script>

<svelte:element this={link ? 'a' : 'div'} href={link || undefined} target={link ? '_blank' : undefined} rel={link ? 'noopener noreferrer' : undefined} class="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg hover:border-primary-300 transition-all group/card no-underline max-w-3xl">
  <div class="flex items-start gap-4">
    <!-- Date badge -->
    <div class="bg-primary-50 text-primary-700 px-3 py-2 rounded-lg text-center min-w-[3.5rem] flex-shrink-0">
      <div class="text-xl font-bold leading-tight">{new Date(event.start_date).getDate()}</div>
      <div class="text-xs font-medium">{new Date(event.start_date).toLocaleString('de-DE', { month: 'short' })}</div>
      {#if event.end_date && new Date(event.start_date).toDateString() !== new Date(event.end_date).toDateString()}
        <div class="text-[0.65rem] mt-1 text-primary-500">+ {Math.ceil((new Date(event.end_date) - new Date(event.start_date)) / (1000 * 60 * 60 * 24))} Tage</div>
      {/if}
    </div>

    <!-- Content -->
    <div class="flex-grow min-w-0">
      <!-- Title -->
      <h3 class="font-semibold text-gray-900 leading-snug mb-1 group-hover/card:text-primary-600 transition-colors">
        {event.title}
      </h3>

      <!-- Metadata -->
      <div class="flex flex-wrap gap-x-3 gap-y-1 text-sm text-gray-500 mb-2">
        {#if startTime}
          <span>{startTime} {#if endTime}– {endTime} {/if}Uhr</span>
        {/if}
        {#if event.location}
          <span>{event.location}</span>
        {:else}
          <span class="text-primary-600 font-medium">Online</span>
        {/if}
        {#if event.cost !== undefined && event.cost !== null && event.cost !== ''}
          <span>
            {#if event.cost === 0 || event.cost === '0' || event.cost === 'kostenlos' || event.cost === 'Kostenlos' || event.cost === 'free' || event.cost === 'Free'}
              Kostenlos
            {:else}
              {typeof event.cost === 'number' ? `${event.cost} €` : event.cost}
            {/if}
          </span>
        {/if}
        {#if event.organizer}
          <span>{event.organizer}</span>
        {/if}
      </div>

      <!-- Description -->
      {#if event.description}
        <p class="mt-1 text-sm text-gray-600">{event.description}</p>
      {/if}

      <!-- Tags -->
      {#if (event.tags && event.tags.length > 0) || (event.category && (!event.tags || !event.tags.length))}
        <div class="flex flex-wrap gap-1.5 mt-3">
          {#if event.tags && event.tags.length > 0}
            {#each event.tags.slice(0, 5) as tag}
              <Tag {tag} groupId={findTagGroup(tag)} selectable={true} selected={($filters.tags || []).includes(tag)} onClick={(e) => toggleTag(tag, e)} />
            {/each}
          {/if}
          {#if event.category && (!event.tags || !event.tags.length)}
            <Tag tag={getCategoryName(event.category)} groupId="topic" selectable={true} selected={($filters.tags || []).includes(getCategoryName(event.category))} onClick={(e) => toggleTag(getCategoryName(event.category), e)} />
          {/if}
        </div>
      {/if}
    </div>
  </div>
</svelte:element>
