<script>
  import "../app.css";
  import { onMount } from "svelte";

  let isDark = false;

  onMount(() => {
    const saved = localStorage.getItem("theme");
    isDark = saved !== null ? saved === "dark" : false;
  });

  function toggleTheme() {
    isDark = !isDark;
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }
</script>

<div class={isDark ? "dark" : ""}>
  <div class="min-h-screen bg-white dark:bg-black transition-colors duration-300">
    <slot />
    <button
      on:click={toggleTheme}
      class="fixed top-4 right-20 z-[3000] p-2 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-white hover:bg-slate-300 dark:hover:bg-slate-600 transition-all duration-200"
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {#if isDark}
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
        </svg>
      {:else}
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      {/if}
    </button>
  </div>
</div>
