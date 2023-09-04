<script lang="ts">
  import { onMount } from "svelte";
  import Card from "$lib/components/Card.svelte";
  import Player from "$lib/components/Player.svelte";

  type CardType = {
    color: string;
    symbol: string;
    id: number;
  };

  let playerCards: CardType[] = [];
  let destinationCard: CardType = { color: "", symbol: "", id: -1 };
  let actualPlayer: number;

  onMount(async () => {
    try {
      let response = await fetch("http://localhost:8082/reset");
      if (response.ok) {
        response = await fetch("http://localhost:8082/game-state");
        if (response.ok) {
          const data = await response.json();
          playerCards = data.cards;
          destinationCard = data.top;
          actualPlayer = data.player;
        }
      }
    } catch (err) {
      console.log(err);
    }
  });

  function setDestinationCard(card: CardType) {
    destinationCard = card;
  }

  let counter = 8;
  function getCard(newCard: CardType) {
    // Animate the original deck card to the player's hand
    const deckCard = document.querySelector(".deck-card") as HTMLElement;
    const playerHand = document.querySelector(".player-hand") as HTMLElement;
    const lastCard = playerHand.lastElementChild as HTMLElement;

    if (!deckCard || !lastCard) return;

    const { top: deckTop, left: deckLeft } = deckCard.getBoundingClientRect();
    const { top: lastCardTop, left: lastCardLeft } =
      lastCard.getBoundingClientRect();

    const translateX = lastCardLeft - deckLeft + 110;
    console.log(lastCardLeft, deckLeft);
    const translateY = lastCardTop - deckTop;

    deckCard.style.transition = "transform 0.5s ease-in-out";
    deckCard.style.transform = `translate(${translateX}px, ${translateY}px)`;

    // Replace the original deck card and add the drawn card to the player's hand
    setTimeout(() => {
      // Reset the original deck card
      deckCard.style.transition = "";
      deckCard.style.transform = "";

      // Add the new card to the player's hand
      playerCards = [...playerCards, newCard];
      counter++;
    }, 500);
  }
</script>

<main class="grid grid-cols-6 grid-rows-[1fr,auto] w-screen h-screen">
  <div class="col-span-6 grid grid-cols-3 grid-rows-3 h-full">
    <div class="row-start-1 col-span-3 h-full">
      <h1 class="p-6 text-6xl font-bold">Kartenmaster</h1>
    </div>
    <div class="row-start-2 col-span-3 flex justify-center items-start gap-6">
      <Card
        color={destinationCard.color}
        number={destinationCard.symbol}
        cardType="destination-card"
      />
      <Card
        isBack={true}
        cardType="deck-card"
        on:action={() => getCard({ color: "blue", symbol: "8", id: counter })}
      />
    </div>
    <div
      class="row-start-3 col-span-3 flex justify-center items-center mx-auto gap-2"
    >
      <Player {setDestinationCard} cards={playerCards} />
    </div>
  </div>
</main>

<div class="overlay grid grid-cols-6 grid-rows-6">
  <div
    class="col-span-2 col-start-3 row-start-4 text-center flex justify-center items-center font-bold text-2xl"
  >
    Player : 0
  </div>
</div>

<style>
  /* Style for the overlay container */
  .overlay {
    position: fixed; /* Use 'absolute' if you want it relative to a parent container */
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -999; /* Adjust the z-index to make sure it's on top of other content */
    pointer-events: none; /* Allow clicks and interactions to pass through */
  }
</style>
