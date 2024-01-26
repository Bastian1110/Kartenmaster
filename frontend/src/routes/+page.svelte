<script lang="ts">
  import {
    Card,
    Player,
    ColorSelect,
    InstructionModal,
    InfoScreen,
  } from "$lib/components";
  import { Confetti } from "svelte-confetti";
  import { onMount } from "svelte";

  type CardInfo = {
    id: number;
    color: string;
    symbol: string;
  };

  type PlayersDict = {
    [key: number]: CardInfo[];
  };

  // Global state of the game
  let playersCards: PlayersDict = {};
  let actualPlayer: number = 0;
  let topCard: CardInfo = { id: -1, color: "blue", symbol: "1" };
  let colorSelection: boolean = false;
  let isActualHuman: boolean = true;
  let virtualGameEnded = false;
  let gameEnded = false;
  let username = "";
  let showInstructionModal = true;
  let winner = "";
  let triggerConfetti = false;
  let actualInfo = "";

  $: if (virtualGameEnded) {
    setTimeout(() => {
      triggerConfetti = true;
      setTimeout(() => {
        gameEnded = true;
        handleEndGame();
        console.log("Winner", winner);
        setTimeout(() => {
          triggerConfetti = false;
        }, 1000);
      }, 1000);
    }, 100);
  }

  // Function to end game and register game data
  const handleEndGame = async () => {
    try {
      let response = await fetch("http://localhost:8082/end-game", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          datetime: new Date().toUTCString(),
        }),
      });
      if (response.ok) {
        const data = await response.json();
        console.log("End Game ", data);
      }
    } catch (err) {
      console.log(err);
    }
  };

  // Animation function for moves
  const cardToTop = (
    id: number,
    playerHandId: number,
    valid: boolean,
    newTop: CardInfo,
  ) => {
    const cardElement = document.querySelector(
      `[data-card-id="${id}"]`,
    ) as HTMLElement;

    const topElement = document.querySelector(".top-card") as HTMLElement;
    if (!cardElement || !topElement) return;

    const { top, left } = topElement.getBoundingClientRect();
    const { top: cardTop, left: cardLeft } =
      cardElement.getBoundingClientRect();

    const translateX = left - cardLeft;
    const translateY = top - cardTop - 18;

    cardElement.style.transition = "transform 1s ease-in-out";
    cardElement.style.transform = `translate(${translateX}px, ${translateY}px)`;
    cardElement.style.zIndex = "10";

    setTimeout(() => {
      if (valid) {
        playersCards[playerHandId] = playersCards[playerHandId].filter(
          (card) => card.id !== id,
        );
        playersCards = { ...playersCards };
        topCard = newTop;
      } else {
        cardElement.style.transition = "";
        cardElement.style.transform = "";
        cardElement.style.zIndex = "1";
      }
      updateGameState();
    }, 1000);
  };

  const stackTohand = (playerHandId: number, newCard: CardInfo) => {
    const stackElement = document.querySelector(".stack-card") as HTMLElement;
    const playerHandElement = document.querySelector(
      `#player-${playerHandId}-container`,
    ) as HTMLElement;
    const lastCard = playerHandElement.lastElementChild as HTMLElement;

    if (!playerHandElement || !stackElement) return;

    const { top, left } = lastCard.getBoundingClientRect();
    const { top: cardTop, left: cardLeft } =
      stackElement.getBoundingClientRect();

    const translateX = left - cardLeft + 130;
    const translateY = top - cardTop - 20;

    stackElement.style.transition = "transform 1s ease-in-out";
    stackElement.style.transform = `translate(${translateX}px, ${translateY}px)`;

    setTimeout(() => {
      playersCards[playerHandId] = [...playersCards[playerHandId], newCard];
      stackElement.style.transition = "transform 0s ease-in-out";
      stackElement.style.transform = "";
      updateGameState();
    }, 1000);
  };

  // Requests to backend
  const createEnv = async () => {
    if (!sessionStorage.getItem("game_started")) {
      try {
        let response = await fetch("http://localhost:8082/start-game", {
          method: "GET",
          credentials: "include",
        });
        if (response.ok) {
          const data = await response.json();
          console.log("Create ", data);
          await resetGame();
          sessionStorage.setItem("game_started", "true");
        }
      } catch (err) {
        console.log(err);
      }
    } else {
      await resetGame(); // Borrar
      await updateGameState();
    }
  };

  const resetGame = async () => {
    try {
      let response = await fetch("http://localhost:8082/reset", {
        method: "GET",
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        console.log("Reset ", data);
        gameEnded = false;
        virtualGameEnded = false;
        actualInfo = "";
        await updateGameState();
      }
    } catch (err) {
      console.log(err);
    }
  };

  const updateGameState = async () => {
    try {
      const response = await fetch("http://localhost:8082/game-state", {
        method: "GET",
        credentials: "include",
      });
      const data = await response.json();
      playersCards = data.players;
      actualPlayer = data.actual;
      topCard = data.top;
      if (actualPlayer == 1) {
        await handleRobotAction();
      }
      if (topCard.color == "ANY") {
        colorSelection = true;
      }
    } catch (err) {
      console.log(err);
    }
  };

  const handleHumanCard = async (id: number, playerHandId: number) => {
    try {
      let response = await fetch("http://localhost:8082/make-action", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action: id }),
      });
      const data = await response.json();
      console.log("Human Action : ", data);
      virtualGameEnded = data.done;
      actualInfo = data.info.message;
      if (virtualGameEnded) {
        winner = username;
      }
      if (response.ok) {
        cardToTop(id, playerHandId, data.info.valid_action, data.info.card);
      }
    } catch (err) {
      console.log(err);
    }
  };

  const handleHumanDraw = async (playerHandId: number) => {
    try {
      let response = await fetch("http://localhost:8082/make-action", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action: 112 }),
      });
      const data = await response.json();
      console.log("Human Draw: ", data);
      virtualGameEnded = data.done;
      actualInfo = data.info.message;
      if (virtualGameEnded) {
        winner = actualPlayer == 0 ? "Kartenmaster" : username;
      }
      stackTohand(playerHandId, data.info.card);
    } catch (err) {
      console.log(err);
    }
  };

  const handleHumanColorSelection = async (color: number) => {
    try {
      let response = await fetch("http://localhost:8082/make-action", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action: color }),
      });
      const data = await response.json();
      console.log("Human Color : ", data);
      virtualGameEnded = data.done;
      actualInfo = data.info.message;
      if (virtualGameEnded) {
        winner = actualPlayer == 0 ? "Kartenmaster" : username;
      }
      setTimeout(() => {
        updateGameState();
        colorSelection = false;
      }, 100);
    } catch (err) {
      console.log(err);
    }
  };

  const handleRobotAction = async () => {
    try {
      let response = await fetch("http://localhost:8082/get-agent-action", {
        method: "GET",
        credentials: "include",
      });
      const data = await response.json();
      console.log("Robot Action: ", data);
      virtualGameEnded = data.done;
      actualInfo = data.info.message;
      if (virtualGameEnded) {
        winner = "Kartenmaster";
      }
      if (
        data.info.type == "normal" ||
        data.info.type == "invalid" ||
        data.info.type == "wild"
      ) {
        setTimeout(() => {
          cardToTop(
            data.info.card.id,
            1,
            data.info.valid_action,
            data.info.card,
          );
        }, 1000);
      }
      if (data.info.type == "draw") {
        setTimeout(() => {
          stackTohand(1, data.info.card);
        }, 500);
      }
      if (data.info.type == "color") {
        setTimeout(() => {
          colorSelection = false;
          updateGameState();
        }, 1000);
      }
    } catch (err) {
      console.log(err);
    }
  };

  onMount(async () => {
    await createEnv();
  });
</script>

{#if gameEnded}
  <main
    class="grid grid-cols-3 grid-rows-3 w-screen h-screen text-white"
    style="grid-template-columns: 20% 60% 20%; grid-template-rows: 20% 60% 20%;"
  >
    <div class="col-start-2 row-start-2 bg-slate-900 rounded-xl flex items-center flex-col justify-center align-middle">
      <h1 class="text-white text-8xl font-bold m-6">
        {winner} Won!
      </h1>
      <div class="mx-6">
        <button
          on:click={resetGame}
          type="submit"
          class="group flex flex-row p-3 text-2xl my-2 font-bold border-2 rounded-lg hover:border-[#696cf0] hover:text-[#696cf0] transition-all duration-200"
        >
          Play Again
          <svg
            class="h-8 w-8 text-white inline-block ml-2 group-hover:rotate-180 transition-all duration-300"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path stroke="none" d="M0 0h24v24H0z" />
            <path d="M9 4.55a8 8 0 0 1 6 14.9m0 -4.45v5h5" />
            <path
              d="M11 19.95a8 8 0 0 1 -5.3 -12.8"
              stroke-dasharray=".001 4.13"
            /></svg
          >
        </button>
      </div>
    </div>
  </main>
{:else}
  <main
    class="grid grid-cols-3 grid-rows-3 w-screen h-screen text-white"
    style="grid-template-columns: 20% 60% 20%;"
  >
    <div class="font-bold text-center row-span-3 text-transparent">A</div>
    <Player
      cards={playersCards[1]}
      playerId={1}
      {actualPlayer}
      enabledReverseHand={true}
    />
    <div class=" font-bold text-center row-span-3 text-transparent">C</div>
    <div class=" font-bold text-center flex items-center justify-center">
      <div class="flex justify-center text-center">
        <Card
          color={topCard.color}
          symbol={topCard.symbol}
          isClickable={false}
          cardType="top-card"
        />
        <div class="relative">
          <Card isBack={true} isClickable={false} />
          <Card
            isBack={true}
            isClickable={false}
            cardType="stack-card relative -ml-[7.73rem] hover:-translate-y-4 hover:translate-x-4 hover:shadow-xl"
            onClick={() => handleHumanDraw(actualPlayer)}
          />
        </div>
      </div>
    </div>

    <Player
      cards={playersCards[0]}
      reverseHand={false}
      onCardClick={handleHumanCard}
      playerId={0}
      enabledReverseHand={true}
      {actualPlayer}
    />
  </main>
{/if}
<div class="absolute bottom-0 right-5 text-white font-mono text-lg">
  Kartenmaster by : <a
    class="underline"
    target="_blank"
    rel="noopener noreferrer"
    href="https://github.com/Bastian1110/Kartenmaster">@Batian1110</a
  >
</div>

<ColorSelect
  show={colorSelection}
  handleSelection={handleHumanColorSelection}
  isClickable={isActualHuman}
/>

<InstructionModal
  on:submit={(event) => {
    username = event.detail.value;
    showInstructionModal = false;
  }}
  show={showInstructionModal}
/>

<InfoScreen info={actualInfo} />

{#if triggerConfetti}
  <div
    style="position: fixed; top: -50px; left: 0; height: 100vh; width: 100vw; display: flex; justify-content: center; overflow: hidden;"
  >
    <Confetti
      x={[-5, 5]}
      y={[0, 0.1]}
      delay={[0, 1500]}
      duration={3000}
      amount={1500}
      fallDistance="100vh"
      size={30}
    />
  </div>
{/if}
