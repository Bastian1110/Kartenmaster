<script>
  export let symbol = "S";
  export let middle = false;
</script>

<span>
  {#if symbol == "S"}
    <svg
      class="text-white {middle ? 'h-10 w-10 font-bold' : 'h-5 w-5'}"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" /></svg
    >
  {:else if symbol == "T"}
    +2
  {:else if symbol == "F"}
    +4
  {:else if symbol == "R"}
    <svg
      class="text-white {middle ? 'h-10 w-10 font-bold' : 'h-5 w-5'}"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <polyline points="23 4 23 10 17 10" />
      <polyline points="1 20 1 14 7 14" />
      <path
        d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"
      /></svg
    >
  {:else if symbol == "ANY"}
    ?
  {:else}
    {symbol}
  {/if}
</span>
