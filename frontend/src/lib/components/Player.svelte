<script lang="ts">
  import Card from "./Card.svelte";

  type CardInfo = {
    id: number;
    color: string;
    symbol: string;
  };

  export let cards: CardInfo[] = [];
  export let reverseHand: boolean = true;
  export let onCardClick = (id: number, playerId: number) => {};
  export let playerId: number;
  export let actualPlayer: number;
</script>

<div class="border-red-400 flex flex-col justify-center">
  <div class="text-center">
    <button on:click={() => (reverseHand = !reverseHand)}>
      {#if reverseHand}
        <svg
          class="h-6 w-6 text-slate-600"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" /></svg
        >
      {:else}
        <svg
          class="h-6 w-6 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
          />
        </svg>
      {/if}
    </button>
  </div>
  <div
    class="font-bold text-center whitespace-nowrap flex items-center justify-center"
  >
    <div
      class="inline-flex {actualPlayer == playerId
        ? ''
        : 'pointer-events-none'}"
      id={`player-${playerId}-container`}
    >
      {#each cards as card (card.id)}
        <Card
          color={card.color}
          symbol={card.symbol}
          isBack={reverseHand}
          data-card-id={card.id}
          onClick={() => onCardClick(card.id, playerId)}
        />
      {/each}
    </div>
  </div>
</div>
