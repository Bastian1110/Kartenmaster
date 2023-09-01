<script lang="ts">
  import Card from "$lib/components/Card.svelte";
  import Player from "$lib/components/Player.svelte";

  let playerCards = [
    { color: "red", number: "6", id: 1 },
    { color: "yellow", number: "1", id: 2 },
    { color: "green", number: "9", id: 3 },
    { color: "blue", number: "+2", id: 6 },
  ];

  function changeCards() {
    playerCards = [
      { color: "blue", number: "7", id: 10 },
      { color: "green", number: "2", id: 11 },
      { color: "red", number: "4", id: 12 },
      { color: "yellow", number: "+4", id: 13 },
      { color: "blue", number: "3", id: 14 },
      { color: "red", number: "3", id: 15 },
    ];
  }

  type CardType = {
    color: string;
    number: string;
    id: number;
  };

  let destinationCard: CardType = { color: "red", number: "4", id: 0 };

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
        number={destinationCard.number}
        cardType="destination-card"
      />
      <Card
        isBack={true}
        cardType="deck-card"
        on:action={() => getCard({ color: "blue", number: "8", id: counter })}
      />
    </div>
    <div
      class="row-start-3 col-span-3 flex justify-center items-center mx-auto gap-2"
    >
      <Player {setDestinationCard} cards={playerCards} />
    </div>
  </div>
</main>
