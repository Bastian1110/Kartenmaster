<script lang="ts">
  import {
    Card,
    Player,
    ColorSelect,
    InstructionModal,
    InfoScreen,
    StarRating,
  } from "$lib/components";
  import { Confetti } from "svelte-confetti";
  import { onMount } from "svelte";
  import { WinnerCat, LooserCat, SadPhone } from "$lib/assets";

  const API = "https://api.kartenmaster.sebastian-mora.site";
  // const API = "http://localhost:8082";

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
  let virtualGameEnded = false; // Change
  let gameEnded = false; // Change
  let username = ""; // Change
  let showInstructionModal = true; // Change
  let winner = "";
  let triggerConfetti = false;
  let actualInfo = "";
  let lastGameRecord = "";
  let lastRating = 0;
  let rated = false;

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
      let response = await fetch(`${API}/end-game`, {
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
        lastGameRecord = data["record_id"];
        console.log("End Game ", data);
      }
    } catch (err) {
      console.log(err);
    }
  };

  // Function to rate the model
  const handleRateModel = async () => {
    try {
      let response = await fetch(`${API}/rate-model`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          rate: lastRating,
          record_id: lastGameRecord,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        console.log("Record Submited ", data);
        rated = true;
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
        let response = await fetch(`${API}/start-game`, {
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
      let response = await fetch(`${API}/reset`, {
        method: "GET",
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        console.log("Reset ", data);
        gameEnded = false;
        virtualGameEnded = false;
        actualInfo = "";
        lastRating = 0;
        rated = false;
        await updateGameState();
      }
    } catch (err) {
      console.log(err);
    }
  };

  const updateGameState = async () => {
    try {
      const response = await fetch(`${API}/game-state`, {
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
      let response = await fetch(`${API}/make-action`, {
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
      let response = await fetch(`${API}/make-action`, {
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
      let response = await fetch(`${API}/make-action`, {
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
      let response = await fetch(`${API}/get-agent-action`, {
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

<div
  class="transition-opacity duration-100 xl:pointer-events-none xl:opacity-0 pointer-events-auto opacity-100"
>
  <div
    class="z-[1000] fixed left-0 top-0 h-full w-full flex bg-slate-800 bg-opacity-80 justify-center align-middle"
  >
    <div
      class="z-[1001] w-[80vw] h-[60vh] md:w-[50vw] md:h-[55vh] col-span-8 col-start-3 my-auto rounded-2xl bg-slate-900 text-white text-center items-center font-mono justify-center align-middle content-center flex flex-col"
    >
      <h2 class="font-bold text-4xl">Too Little!</h2>
      <p class="text-lg m-2">
        Kartenmaster its not designed to work on small screens, so please make
        the window bigger!
      </p>
      <span class="text-sm"
        >(If you are playing on mobile, please try on your laptop)</span
      >
      <img src={SadPhone} alt="cat" class="w-[16rem] h-[16rem]" />
    </div>
  </div>
</div>

{#if gameEnded}
  <main
    class="grid grid-cols-3 grid-rows-3 w-screen h-screen text-white"
    style="grid-template-columns: 20% 60% 20%; grid-template-rows: 20% 60% 20%;"
  >
    <div
      class="col-start-2 row-start-2 bg-slate-900 rounded-xl flex items-center flex-row justify-center align-middle"
    >
      <div class="flex flex-1 w-[50%]">
        <img
          src={winner == "Kartenmaster" ? WinnerCat : LooserCat}
          alt="cat"
          class="w-full"
        />
      </div>
      <div class="flex flex-1 w-[50%] flex-col items-center">
        <h1 class="text-white text-6xl font-bold m-6">
          {winner} Won!
        </h1>
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
        <button
          on:click={handleRateModel}
          type="submit"
          disabled={lastRating === 0 ? true : false}
          class={`flex flex-row p-3 text-2xl my-2 font-bold border-2 rounded-lg  ${
            lastRating === 0
              ? "text-slate-500 border-slate-500"
              : "group hover:border-[#696cf0] hover:text-[#696cf0] transition-all duration-200"
          }`}
        >
          Rate KartenMaster
          <svg
            class={`h-8 w-8 group-hover:text-[#696cf0] inline-block ml-2 transition-all duration-300 ${
              lastRating === 0 ? "text-slate-500" : "text-white"
            } ${rated ? "border-emerald-500 text-emerald-300" : ""}`}
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
            <path
              d="M7 11v 8a1 1 0 0 1 -1 1h-2a1 1 0 0 1 -1 -1v-7a1 1 0 0 1 1 -1h3a4 4 0 0 0 4 -4v-1a2 2 0 0 1 4 0v5h3a2 2 0 0 1 2 2l-1 5a2 3 0 0 1 -2 2h-7a3 3 0 0 1 -3 -3"
            /></svg
          >
        </button>
        <StarRating bind:rating={lastRating} />
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
  Kartenmaster, 2024 by : <a
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
