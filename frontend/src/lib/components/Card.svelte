<script lang="ts">
  import Special from "./Special.svelte";
  export let symbol: string = "+2"; // Default to Spade symbol
  export let color: string = "red"; // Default to black color
  export let isBack: boolean = false;
  export let isClickable: boolean = true;
  export let cardType: string = "normal-card";
  export let onClick = () => {};

  type ColorsDict = {
    [key: string]: string;
  };

  const colors: ColorsDict = {
    red: "#f43f5e",
    blue: "#6366f1",
    yellow: "#eab308",
    green: "#14b8a6",
    ANY: "#6d28d9",
  };

  let flipClass = "";

  $: flipClass = isBack ? "flipped" : "";
</script>

<div
  {...$$props}
  role="button"
  tabindex="0"
  on:click={onClick}
  class="{cardType} flip-card relative w-28 h-40 rounded-lg text-white font-bold inline-block mx-2 transition-all duration-200 {isClickable
    ? 'hover:-translate-y-4 hover:shadow-xl'
    : ''}"
>
  <div class="flip-card-inner {flipClass}">
    <div
      class="flip-card-front rounded-lg"
      style="background-color:{colors[color]};"
    >
      <div class="absolute top-1 left-1">
        <Special {symbol} />
      </div>
      <div
        class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-4xl"
      >
        <Special {symbol} middle={true} />
      </div>
      <div class="absolute bottom-1 right-1">
        <Special {symbol} />
      </div>
    </div>
    <div
      class="flip-card-back rounded-lg bg-slate-800 text-center align-middle"
    >
      <div class="text-4xl mt-[50%]">UNO</div>
    </div>
  </div>
</div>

<style>
  .flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.5s;
    transform-style: preserve-3d;
  }

  .flip-card-inner.flipped {
    transform: rotateY(180deg);
  }

  .flip-card-front,
  .flip-card-back {
    color: white;
    position: absolute;
    width: 100%;
    height: 100%;
    -webkit-backface-visibility: hidden; /* Safari */
    backface-visibility: hidden;
  }

  .flip-card-back {
    transform: rotateY(180deg);
  }
</style>
