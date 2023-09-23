<script lang="ts">
  import { Card, Player, ColorSelect } from "$lib/components";
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
  let humanColorSelection: boolean = false;

  // Test State for the
  let colorFlag = false;
  let change = false;
  let counter = 0;
  let playerTest = 0;
  function addTestCard(playerId: number) {
    const colors = ["red", "blue", "yellow", "green"];
    const randomIndex = Math.floor(Math.random() * colors.length);
    const randomColor = colors[randomIndex];
    const randomNumber = Math.floor(Math.random() * 9);
    const newCard: CardInfo = {
      id: counter,
      color: randomColor,
      symbol: randomNumber.toString(),
    };
    playersCards[playerId] = [...playersCards[playerId], newCard];
    counter++;
  }

  // Animation function for moves

  const cardToTop = (
    id: number,
    playerHandId: number,
    valid: boolean,
    newTop: CardInfo
  ) => {
    const cardElement = document.querySelector(
      `[data-card-id="${id}"]`
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

    setTimeout(() => {
      if (valid) {
        playersCards[playerHandId] = playersCards[playerHandId].filter(
          (card) => card.id !== id
        );
        playersCards = { ...playersCards };
        topCard = newTop;
      } else {
        cardElement.style.transition = "";
        cardElement.style.transform = "";
      }
      updateGameState();
    }, 1000);
  };

  const stackTohand = (playerHandId: number, newCard: CardInfo) => {
    const stackElement = document.querySelector(".stack-card") as HTMLElement;
    const playerHandElement = document.querySelector(
      `#player-${playerHandId}-container`
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
      if (topCard.color == "ANY" && actualPlayer != 1) {
        humanColorSelection = true;
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
      setTimeout(() => {
        updateGameState();
        humanColorSelection = false;
      }, 1000);
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
            data.info.card
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
          updateGameState();
        }, 500);
      }
    } catch (err) {
      console.log(err);
    }
  };

  onMount(async () => {
    await createEnv();
  });
</script>

<main
  class="grid grid-cols-3 grid-rows-3 w-screen h-screen text-white"
  style="grid-template-columns: 20% 60% 20%;"
>
  <div class=" font-bold text-center row-span-3">
    A <button
      on:click={() => {
        colorFlag = !colorFlag;
      }}>TEst</button
    >
  </div>
  <Player cards={playersCards[1]} playerId={1} {actualPlayer} />
  <div class=" font-bold text-center row-span-3">C</div>
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
    {actualPlayer}
  />
</main>

<ColorSelect
  show={humanColorSelection}
  handleSelection={handleHumanColorSelection}
/>
