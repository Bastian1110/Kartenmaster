<script lang="ts">
  export let isClickable: boolean;
  export let show: boolean = false;
  export let handleSelection = (color: number) => {};
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
      class="z-[1000] col-span-6 col-start-4 my-auto rounded-2xl bg-slate-900 text-center shadow-lg {isClickable
        ? ''
        : 'pointer-events-none'}"
    >
      <h1 class="m-8 mb-0 text-4xl font-bold text-white">Choose a color!</h1>
      <div class="flex justify-around items-center mt-8 mb-8">
        <button
          on:click={() => handleSelection(109)}
          class="bg-[#6366f1] rounded-full w-[8rem] h-[8rem] hover:scale-105 hover:border-2 hover:border-[#696cf0] transition-all duration-150"
        />
        <button
          on:click={() => handleSelection(108)}
          class="bg-[#f43f5e] rounded-full w-[8rem] h-[8rem] hover:scale-105 hover:border-2 hover:border-[#f1536d] transition-all duration-150"
        />
        <button
          on:click={() => handleSelection(107)}
          class="bg-[#14b8a6] rounded-full w-[8rem] h-[8rem] hover:scale-105 hover:border-2 hover:border-[#27dfc9] transition-all duration-150"
        />
        <button
          on:click={() => handleSelection(106)}
          class="bg-[#eab308] rounded-full w-[8rem] h-[8rem] hover:scale-105 hover:border-2 hover:border-[#ead308] transition-all duration-150"
        />
      </div>
    </div>
  </div>
</div>
