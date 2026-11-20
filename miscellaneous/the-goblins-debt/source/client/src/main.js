import Phaser from "phaser";
import "./styles.css";
import { GameScene } from "./scenes/GameScene.js";
import { gameApi } from "./services/gameApi.js";
import { Sound } from "./systems/audio.js";
const $ = (id) => document.getElementById(id);
function show(id, value = true) {
  const element = $(id);
  if (element.hidden === value) element.hidden = !value;
}
let scene,
  connected = false,
  progress = { balance: 0, unlocked: false },
  busy = false,
  dialogueOpen = false,
  gameStarted = false,
  rewardFlag = "",
  toastTimer;
const sound = new Sound();
const ui = {
  sound,
  ready(s) {
    scene = s;
    s.reduced = $("reduced").checked;
    $("play").disabled = !connected;
  },
  wallet(n) {
    $("wallet").innerHTML = `${n} <em>/ 23</em>`;
  },
  toast(message) {
    $("toast").textContent = message;
    $("toast").classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => $("toast").classList.remove("visible"), 4200);
  },
  nearGuardian(near) {
    show("interact", near && !dialogueOpen && !busy);
  },
  region(name) {
    if ($("region").textContent !== name) $("region").textContent = name;
  },
  escape() {
    if (!$("help").hidden) {
      show("help", false);
      return;
    }
    if (!gameStarted || scene.victorious || busy) return;
    if (dialogueOpen) {
      closeDialogue();
      return;
    }
    pause(!scene.paused);
  },
  interact: interact,
  victory() {
    show("dialogue", false);
    show("interact", false);
    show("victory");
    loadReward();
  },
};
const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: "game",
  width: 1280,
  height: 720,
  backgroundColor: "#244769",
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  physics: {
    default: "arcade",
    arcade: { gravity: { y: 1050 }, debug: false },
  },
  render: { antialias: true, roundPixels: false },
  fps: { target: 60 },
  scene: [new GameScene(ui)],
});
function applyProgress(data) {
  progress = data;
  $("ledger").innerHTML = `${data.balance} <em>/ 120</em>`;
  $("ledger-fill").style.width = `${(data.balance / 120) * 100}%`;
  if (data.unlocked && gameStarted && scene && !scene.victorious)
    scene.openVault();
}
async function connect() {
  try {
    applyProgress(await gameApi.progress());
    connected = true;
    $("connection").textContent = "The guardian is waiting.";
    $("play").disabled = !scene;
  } catch (e) {
    $("connection").textContent = `${e.message} Click to retry.`;
    $("play").disabled = true;
  }
}
$("play").disabled = true;
connect();
$("connection").onclick = connect;
$("play").onclick = () => {
  if (!connected || !scene) return;
  sound.unlock();
  show("menu", false);
  show("hud");
  show("region");
  show("bottom-controls");
  gameStarted = true;
  scene.start();
  if (progress.unlocked) scene.openVault();
  else ui.toast("Follow the old road. Bring back 23 gold pieces.");
};
$("how").onclick = () => show("help");
$("help-close").onclick = () => show("help", false);
function pause(value) {
  scene.setPaused(value);
  show("pause", value);
  show("interact", false);
  if (!value) sync();
}
$("pause-button").onclick = () => ui.escape();
$("resume").onclick = () => pause(false);
$("return-menu").onclick = () => {
  show("pause", false);
  show("menu");
  show("hud", false);
  show("region", false);
  show("bottom-controls", false);
  gameStarted = false;
  scene.playing = false;
  scene.setPaused(true);
};
$("sound").checked = localStorage.getItem("goblins-sound") === "true";
sound.enabled = $("sound").checked;
$("sound").onchange = (e) => {
  sound.enabled = e.target.checked;
  sound.unlock();
  localStorage.setItem("goblins-sound", sound.enabled);
};
$("reduced").checked = localStorage.getItem("goblins-reduced") === "true";
$("reduced").onchange = (e) => {
  if (scene) scene.reduced = e.target.checked;
  localStorage.setItem("goblins-reduced", e.target.checked);
};
game.events.on("ready", () => {
  if (scene) scene.reduced = $("reduced").checked;
});
function say(text) {
  dialogueOpen = true;
  show("interact", false);
  $("dialogue-text").textContent = text;
  show("dialogue");
  scene.setPaused(true);
  scene.guardian.play("goblin-talk");
  sound.play("talk");
}
function closeDialogue() {
  if (busy) return;
  show("dialogue", false);
  dialogueOpen = false;
  scene.guardian.play("goblin-idle");
  scene.setPaused(false);
}
$("dialogue-close").onclick = closeDialogue;
async function interact() {
  if (busy || !$("pause").hidden) return;
  if (dialogueOpen) {
    closeDialogue();
    return;
  }
  if (scene.wallet < 23) {
    const first = !sessionStorage.getItem("guardian-met");
    sessionStorage.setItem("guardian-met", "yes");
    say(
      first
        ? "Gold, traveler. One hundred and twenty pieces of it. Not a coin less. Bring me your earnings, and perhaps the vault shall open. I trust gold more than my own eyes."
        : scene.wallet === 0
          ? "You return empty-handed? My vault does not open for promises. I trust gold more than my own eyes."
          : "Your pouch isn't full yet. There is more gold in the forest.",
    );
    return;
  }
  busy = true;
  say("Twenty-three pieces? Very well. Into the ledger they go.");
  scene.guardian.play("goblin-deposit");
  $("dialogue-close").disabled = true;
  try {
    const data = await gameApi.deposit(23);
    scene.respawnCoins();
    sound.play("deposit");
    applyProgress(data);
    $("dialogue-text").textContent = data.unlocked
      ? "One hundred and twenty. The debt is paid."
      : `${data.balance} pieces in the ledger. The forest is generous. Go on, then.`;
  } catch (e) {
    $("dialogue-text").textContent =
      `The ledger could not be reached. Your pouch is safe. ${e.message}`;
  } finally {
    busy = false;
    $("dialogue-close").disabled = false;
  }
}
async function sync() {
  if (!connected || busy) return;
  try {
    applyProgress(await gameApi.progress());
  } catch {}
}
setInterval(() => {
  if (gameStarted && !document.hidden && !scene.victorious) sync();
}, 10000);
async function loadReward() {
  show("retry-reward", false);
  $("reward-error").textContent = "";
  try {
    const data = await gameApi.reward();
    rewardFlag = data.flag;
    $("flag").textContent = data.flag;
    show("copy");
  } catch (e) {
    $("flag").textContent = "The vault is unlocked. Your reward is safe.";
    $("reward-error").textContent = e.message;
    show("retry-reward");
  }
}
$("retry-reward").onclick = loadReward;
$("copy").onclick = async () => {
  try {
    await navigator.clipboard.writeText(rewardFlag);
    $("copy").textContent = "Copied to clipboard";
  } catch {
    $("reward-error").textContent =
      "Select the flag above and copy it with Ctrl+C.";
  }
};
document.addEventListener("visibilitychange", () => {
  if (
    document.hidden &&
    gameStarted &&
    !scene.victorious &&
    !busy &&
    !dialogueOpen
  )
    pause(true);
});
window.addEventListener("blur", () => {
  if (gameStarted && !scene.victorious && !busy && !dialogueOpen) pause(true);
});
// DOM UI must remain operable even while the physics world is paused.
window.addEventListener("keydown", (event) => {
  if (event.repeat) return;
  if (event.code === "Escape" && !event.repeat) {
    event.preventDefault();
    ui.escape();
  }
  if (!gameStarted || !scene || scene.victorious) return;
  if (event.code === "KeyE" && Math.abs(scene.player.x - 292) < 150) {
    event.preventDefault();
    interact();
  }
  if (!scene.paused && ["Space", "KeyW", "ArrowUp"].includes(event.code)) {
    event.preventDefault();
    scene.jumpAt = scene.time.now;
  }
});
if (import.meta.env.VITE_TEST_MODE === "true") window.__game = game;
