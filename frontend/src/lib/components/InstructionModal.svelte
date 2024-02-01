<script lang="ts">
  import { UnoCat } from "$lib/assets";
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  let nametag = '';
  function handleSubmit() {
    dispatch('submit', { value: nametag });
  }

  export let show: boolean = false;
</script>

<div
  class={`transition-opacity duration-500 ${
    !show ? "pointer-events-none opacity-0 " : "pointer-events-auto opacity-100"
  }`}
>
  <div
    class="z-[100] fixed left-0 top-0 grid h-full w-full grid-cols-12 bg-slate-900 bg-opacity-50"
  >
    <div
      class="z-[1000] col-span-8 col-start-3 my-auto rounded-2xl bg-slate-900 text-center shadow-lg font-mono"
    >
      <div class="flex flex-row">
        <h1 class="flex-1 m-8 mb-0 text-4xl font-bold  text-white text-left">
          Welcome to KartenMaster !
        </h1>
      </div>
      <div class="flex flex-row mt-8 mb-8 text-white text-left">
        <div
          class="text-left w-full font-[500] text-lg mx-8 align-center justify-center"
        >
          Hello! This is Kartenmaster, a Reinforcement Learning agent trying to
          get good at playing UNO, Kartenmaster can't see your cards, or can
          only see the top card and his own cards.
        </div>
        <form on:submit|preventDefault={handleSubmit} class="w-full flex flex-col justify-start">
          <h2 class="font-bold text-2xl my-2">Enter you username!</h2>
          <input
            bind:value={nametag}
            placeholder="- GAL -"
            class="bg-slate-900 text-xl border-white border-2 rounded-lg p-3 w-[80%] text-center my-2"
          />
          <button
            type="submit"
            class="p-3 text-xl my-2 w-[80%] font-bold border-2 rounded-lg hover:border-[#696cf0] hover:text-[#696cf0] transition-all duration-200"
          >
            Let's Play
          </button>
        </form>
      </div>
    </div>
  </div>
</div>
