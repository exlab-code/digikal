<script>
  export let tag;
  export let groupId = null;
  export let selectable = false;
  export let selected = false;
  export let count = null;
  export let onClick = () => {};
  
  // Generate CSS classes
  $: classes = [
    'tag',
    groupId ? `tag-${groupId}` : '',
    selectable ? 'selectable' : '',
    selected ? 'selected' : ''
  ].filter(Boolean).join(' ');
</script>

<button
  class={classes}
  on:click={onClick}
  type="button"
  title={tag}
>
  <span class="tag-text">{tag}</span>
  {#if count !== null && count > 1}
    <span class="tag-count">{count}</span>
  {/if}
</button>
