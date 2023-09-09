<script lang="ts">
  import { onMount } from "svelte";
  import { Confetti } from "svelte-confetti";
  import { Card, Player } from "$lib/components";

  const numberToColor: { [key: number]: string } = {
    108: "red",
    109: "green",
    110: "blue",
    111: "yellow",
  };

  type CardType = {
    color: string;
    symbol: string;
    id: number;
  };

  let winner = false;

  let chooseColorFlag = false;

  let playerCards: CardType[] = [];
  let top: CardType = { color: "", symbol: "", id: -1 };
  let actualPlayer: number;

  const updateGameState = async () => {
    try {
      const response = await fetch("http://localhost:8082/game-state", {
        method: "GET",
        credentials: "include", // this is the important part
      });
      const data = await response.json();
      playerCards = data.cards;
      top = data.top;
      actualPlayer = data.player;
      if (top.color == "ANY") {
        chooseColorFlag = true;
      }
      console.log("Game state updated!");
    } catch (err) {
      console.log(err);
    }
  };

  const createEnv = async () => {
    try {
      let response = await fetch("http://localhost:8082/start-game", {
        method: "GET",
        credentials: "include", // this is the important part
      });
      if (response.ok) {
        const data = await response.json();
        console.log(data);
        await resetGame();
      }
    } catch (err) {
      console.log(err);
    }
  };

  const resetGame = async () => {
    try {
      let response = await fetch("http://localhost:8082/reset", {
        method: "GET",
        credentials: "include", // this is the important part
      });
      if (response.ok) {
        await updateGameState();
      }
    } catch (err) {
      console.log(err);
    }
  };

  onMount(async () => {
    await createEnv();
  });

  const handleAction = async (action: number) => {
    try {
      let response = await fetch("http://localhost:8082/make-action", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action }),
      });
      let data = await response.json();
      winner = data.done;
      if (action == 112) {
        getCard(data.info.card);
      } else if (action >= 108 && action <= 111) {
        top.color = numberToColor[action];
        chooseColorFlag = false;
        updateGameState();
      } else {
        updateGameState();
      }
    } catch (err) {
      console.log(err);
    }
  };

  function setTopCard(card: CardType) {
    top = card;
  }

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
    const translateY = lastCardTop - deckTop;

    deckCard.style.transition = "transform 0.5s ease-in-out";
    deckCard.style.transform = `translate(${translateX}px, ${translateY}px)`;

    // Replace the original deck card and add the drawn card to the player's hand
    setTimeout(async () => {
      // Add the new card to the player's hand
      playerCards = [...playerCards, newCard];
      deckCard.style.transition = "";
      deckCard.style.transform = "";
      await updateGameState();
    }, 500);
  }
</script>

<main class="grid grid-cols-6 grid-rows-[1fr,auto] w-screen h-screen">
  <div class="col-span-6 grid grid-cols-3 grid-rows-3 h-full">
    <div class="row-start-1 col-span-3 h-full">
      <h1 class="p-6 text-6xl font-bold">Kartenmaster</h1>
    </div>
    <div class="row-start-2 col-span-3 flex justify-center items-start gap-6">
      <Card color={top.color} number={top.symbol} cardType="destination-card" />
      <Card
        isBack={true}
        cardType="deck-card"
        on:action={() => handleAction(112)}
      />
    </div>
    <div
      class="row-start-3 col-span-3 flex justify-center items-center mx-auto gap-2"
    >
      <Player
        handleCardSelection={handleAction}
        {setTopCard}
        cards={playerCards}
      />
    </div>
  </div>
</main>

<div class="overlay grid grid-cols-6 grid-rows-6">
  <div
    class="col-span-2 col-start-3 row-start-4 text-center flex justify-center items-center font-bold text-2xl"
  >
    Player : {actualPlayer}
  </div>
</div>

<div
  class={` transition-opacity duration-500 ${
    !chooseColorFlag
      ? "pointer-events-none opacity-0 "
      : "pointer-events-auto opacity-100"
  }`}
>
  <div
    class="z-[100] fixed -left-0 top-0 grid h-full w-full grid-cols-12 bg-slate-600 bg-opacity-90"
  >
    <div
      class=" z-[1000] col-span-6 col-start-4 my-[8rem] rounded-2xl bg-white text-start shadow-lg"
    >
      <h1 class="row-span-1 m-8 mb-0 text-4xl font-bold">Choose a color!</h1>
      <div class="grid grid-cols-2 gap-4">
        <div class="text-center align-middle flex justify-center pt-6">
          <button
            on:click={() => handleAction(109)}
            class="bg-blue-500 rounded-full w-[9rem] h-[9rem]"
          />
        </div>
        <div class="text-center align-middle flex justify-center pt-6">
          <button
            on:click={() => handleAction(108)}
            class="bg-red-500 rounded-full w-[9rem] h-[9rem]"
          />
        </div>
        <div class="text-center align-middle flex justify-center py-4">
          <button
            on:click={() => handleAction(111)}
            class="bg-green-500 rounded-full w-[9rem] h-[9rem]"
          />
        </div>
        <div class="text-center align-middle flex justify-center py-4">
          <button
            on:click={() => handleAction(110)}
            class="bg-yellow-500 rounded-full w-[9rem] h-[9rem]"
          />
        </div>
      </div>
    </div>
  </div>
</div>

{#if winner}
  <div
    style="position: fixed; top: -50px; left: 0; height: 100vh; width: 100vw; display: flex; justify-content: center; overflow: hidden;"
  >
    <Confetti
      x={[-5, 5]}
      y={[0, 0.1]}
      delay={[0, 1500]}
      duration={2000}
      amount={1000}
      fallDistance="70vh"
      size={30}
    />
  </div>
{/if}

<style>
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
