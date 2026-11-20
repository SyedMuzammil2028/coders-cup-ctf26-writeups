import Phaser from "phaser";
import { makeArt } from "../systems/art.js";
import {
  WORLD_WIDTH,
  GROUND_Y,
  SPEED,
  platforms,
  coinPositions,
  hazards,
} from "../systems/level.js";
export class GameScene extends Phaser.Scene {
  constructor(ui) {
    super("forest");
    this.ui = ui;
    this.playing = false;
    this.paused = false;
    this.wallet = 0;
    this.facing = 1;
    this.lastGround = -1000;
    this.jumpAt = -1000;
    this.landUntil = 0;
    this.reduced = false;
    this.victorious = false;
  }
  preload() {
    this.load.image(
      "vista",
      new URL("../../assets/vista.webp", import.meta.url).href,
    );
    this.load.image(
      "crimson-tree",
      new URL("../../assets/crimson-tree.webp", import.meta.url).href,
    );
  }
  create() {
    makeArt(this);
    this.world();
    this.physics.world.setBounds(0, 0, WORLD_WIDTH, 900);
    this.ground = this.physics.add.staticGroup();
    // Collision matches the visible moss surface; all gameplay objects scroll 1:1.
    for (let x = 0; x < WORLD_WIDTH; x += 256) {
      const w = Math.min(256, WORLD_WIDTH - x);
      this.add
        .tileSprite(x, GROUND_Y, w, 240, "stone")
        .setOrigin(0)
        .setDepth(2);
      const b = this.add.rectangle(x + w / 2, GROUND_Y + 100, w, 200, 0, 0);
      this.physics.add.existing(b, true);
      this.ground.add(b);
    }
    for (const p of platforms) {
      this.add
        .image(p.x, p.y, "ledge")
        .setOrigin(0)
        .setDisplaySize(p.width, 64)
        .setDepth(3);
      const b = this.add.rectangle(
        p.x + p.width / 2,
        p.y + 10,
        p.width,
        20,
        0,
        0,
      );
      this.physics.add.existing(b, true);
      b.body.checkCollision.down = false;
      b.body.checkCollision.left = false;
      b.body.checkCollision.right = false;
      this.ground.add(b);
    }
    this.player = this.physics.add
      .sprite(480, GROUND_Y - 7, "hero-idle", 0)
      .setOrigin(0.5, 0.93)
      .setScale(0.73)
      .setDepth(6);
    this.player.body.setSize(34, 94).setOffset(47, 25);
    this.player
      .setCollideWorldBounds(true)
      .setMaxVelocity(SPEED, 850)
      .setDragX(1900);
    this.player.play("idle");
    this.physics.add.collider(this.player, this.ground);
    this.guardian = this.add
      .sprite(292, GROUND_Y, "goblin-idle", 0)
      .setOrigin(0.5, 192 / 208)
      .setScale(0.84)
      .setDepth(5)
      .play("goblin-idle");
    this.coins = this.physics.add.staticGroup();
    this.coinSprites = [];
    coinPositions.forEach((p, i) => {
      const coin = this.coins
        .create(p.x, p.y, "coin")
        .setScale(0.65)
        .setDepth(5);
      coin.refreshBody();
      coin.body.setCircle(16, 4, 4);
      coin.baseY = p.y;
      coin.coinIndex = i;
      this.coinSprites.push(coin);
    });
    this.physics.add.overlap(this.player, this.coins, (_, coin) => {
      if (!this.playing || this.paused || this.victorious || !coin.active)
        return;
      coin.disableBody(true, true);
      this.wallet++;
      this.ui.wallet(this.wallet);
      this.ui.sound.play("coin");
      this.spark(coin.x, coin.y);
      if (this.wallet === 23)
        this.ui.toast("Your pouch is full. Return to the guardian.");
    });
    this.hazardGroup = this.physics.add.staticGroup();
    for (const x of hazards) {
      const h = this.add.graphics().setDepth(4);
      h.fillStyle(0x883e49);
      h.fillTriangle(x - 24, GROUND_Y, x - 14, GROUND_Y - 23, x - 3, GROUND_Y);
      h.fillTriangle(x - 3, GROUND_Y, x + 8, GROUND_Y - 30, x + 22, GROUND_Y);
      h.lineStyle(2, 0xc17865, 0.7);
      h.lineBetween(x - 14, GROUND_Y - 23, x - 7, GROUND_Y - 7);
      const b = this.add.rectangle(x, GROUND_Y - 10, 38, 20, 0, 0);
      this.physics.add.existing(b, true);
      this.hazardGroup.add(b);
    }
    this.physics.add.overlap(this.player, this.hazardGroup, () => {
      if (
        this.time.now < (this.hurtUntil || 0) ||
        !this.playing ||
        this.paused ||
        this.victorious
      )
        return;
      this.hurtUntil = this.time.now + 1400;
      this.player.setVelocity(-this.facing * 130, -300);
      this.player.x -= this.facing * 60;
      this.ui.toast("Thorn roots. A small jump will do.");
      this.tweens.add({
        targets: this.player,
        alpha: 0.3,
        yoyo: true,
        repeat: 3,
        duration: 130,
        onComplete: () => this.player.setAlpha(1),
      });
    });
    this.keys = this.input.keyboard.addKeys({
      left: "A",
      right: "D",
      up: "W",
      jump: "SPACE",
      interact: "E",
      esc: "ESC",
      arrowLeft: "LEFT",
      arrowRight: "RIGHT",
      arrowUp: "UP",
    });
    this.cameras.main.setBounds(0, 0, WORLD_WIDTH, 720);
    this.cameras.main.setScroll(0, 0);
    this.cameraX = 0;
    this.look = 70;
    this.physics.pause();
    this.ui.ready(this);
  }
  world() {
    this.add
      .rectangle(0, 0, 1280, 720, 0x294b72)
      .setOrigin(0)
      .setScrollFactor(0)
      .setDepth(-20);
    this.add
      .image(750, 400, "vista")
      .setDisplaySize(2200, 1467)
      .setScrollFactor(0.025, 0)
      .setDepth(-19)
      .setAlpha(0.85);
    // Seamless, separate depth bands rather than copies of a flattened scene.
    this.sway = [];
    this.lights = [];
    for (let layer = 0; layer < 3; layer++) {
      const factor = [0.22, 0.44, 0.72][layer],
        spacing = [560, 840, 1120][layer];
      for (let x = -500; x < WORLD_WIDTH * factor + 1800; x += spacing) {
        const tree = this.add
          .image(
            x + Math.sin(x) * 90,
            620,
            layer === 0 ? "tree-0" : "crimson-tree",
          )
          .setOrigin(0.5, 1)
          .setScrollFactor(factor, 0)
          .setDepth(-14 + layer * 3)
          .setScale([1.12, 0.82, 1.1][layer])
          .setAlpha([0.28, 0.38, 0.9][layer]);
        if (layer === 1) tree.setTint(0x637d9b);
        if (layer > 0) tree.setFlipX(Math.round(x / spacing) % 2 === 0);
        this.sway.push(tree);
      }
    }
    for (let x = 700; x < WORLD_WIDTH; x += 670) {
      this.add
        .image(x, GROUND_Y + 5, "bush")
        .setOrigin(0.5, 1)
        .setScale(0.7 + Math.sin(x) * 0.15)
        .setDepth(3);
      if (x % 3 < 2)
        this.add
          .image(x + 120, GROUND_Y + 1, "mushroom")
          .setOrigin(0.5, 1)
          .setScale(0.55)
          .setDepth(4);
    }
    this.gateArt();
    this.watchtower();
    for (let x = 550; x < WORLD_WIDTH; x += 1450)
      this.lantern(x, GROUND_Y - 170);
    for (let x = -100; x < WORLD_WIDTH * 1.1 + 1400; x += 1250) {
      const fern = this.add
        .image(x, 770, "fern")
        .setOrigin(0.5, 1)
        .setScale(1)
        .setScrollFactor(1.12, 0)
        .setDepth(9)
        .setAlpha(0.65);
      this.sway.push(fern);
    }
    // Animated waterfall at an original forest landmark, behind all terrain.
    const water = this.add.graphics().setDepth(-5);
    this.water = water;
    this.waterX = 6020;
    this.distantWater = this.add
      .graphics()
      .setScrollFactor(0.025, 0)
      .setDepth(-18);
    const mist = this.add.graphics().setScrollFactor(0.35, 0).setDepth(-3);
    mist.fillStyle(0x95b7c5, 0.045);
    for (let i = 0; i < 7; i++)
      mist.fillEllipse(400 + i * 920, 530 + (i % 2) * 40, 1000, 100);
    this.mist = mist;
    this.motes = Array.from({ length: 36 }, (_, i) =>
      this.add
        .image((i * 421) % 1600, 140 + ((i * 137) % 460), "mote")
        .setScrollFactor(0)
        .setAlpha(0.15 + (i % 4) * 0.1)
        .setDepth(10),
    );
  }
  gateArt() {
    const g = this.add.graphics().setDepth(1);
    g.fillStyle(0x243242);
    g.fillRoundedRect(35, 220, 290, 382, 8);
    g.lineStyle(3, 0x65706a, 0.6);
    for (let y = 240; y < 600; y += 42) g.lineBetween(35, y, 325, y);
    for (let y = 240; y < 600; y += 42)
      for (let x = 35 + (y % 84 === 0 ? 0 : 35); x < 325; x += 70)
        g.lineBetween(x, y, x, y + 42);
    g.fillStyle(0x111e30);
    g.fillRoundedRect(95, 288, 170, 315, { tl: 84, tr: 84, bl: 0, br: 0 });
    g.lineStyle(14, 0x4c5660);
    g.strokeRoundedRect(90, 277, 180, 332, { tl: 90, tr: 90, bl: 0, br: 0 });
    this.door = this.add.graphics().setDepth(2);
    this.door.fillStyle(0x152638);
    this.door.fillRoundedRect(105, 302, 150, 300, {
      tl: 74,
      tr: 74,
      bl: 0,
      br: 0,
    });
    this.door.lineStyle(2, 0xa18c5c, 0.6);
    for (let x = 120; x < 250; x += 22) this.door.lineBetween(x, 345, x, 596);
    this.door.lineStyle(2, 0xcead72, 0.8);
    this.door.strokeCircle(180, 431, 24);
    this.door.lineBetween(180, 408, 180, 454);
    this.door.lineBetween(158, 431, 202, 431);
    g.fillStyle(0x81904d);
    for (let i = 0; i < 18; i++)
      g.fillEllipse(45 + i * 16, 223 + Math.sin(i) * 7, 30, 12);
    // The guardian's counting desk and ledger.
    g.fillStyle(0x5b3e32);
    g.fillRect(315, 566, 78, 8);
    g.fillRect(323, 571, 6, 31);
    g.fillRect(380, 571, 6, 31);
    g.fillStyle(0xb5aa8b);
    g.fillTriangle(329, 561, 352, 554, 352, 566);
    g.fillTriangle(353, 554, 375, 560, 353, 566);
    g.lineStyle(1, 0x776b4f);
    g.lineBetween(354, 555, 354, 566);
    this.add
      .text(180, 245, "THE SEALED VAULT", {
        fontFamily: "Georgia",
        fontSize: 10,
        color: "#d0bf91",
        letterSpacing: 2,
      })
      .setOrigin(0.5)
      .setDepth(3);
    this.lantern(62, 365);
    this.lantern(309, 365);
  }
  watchtower() {
    const x = 13650,
      g = this.add.graphics().setDepth(0);
    g.fillStyle(0x29394a);
    g.fillRect(x - 180, 230, 320, 372);
    g.fillTriangle(x - 180, 230, x - 155, 198, x - 120, 230);
    g.fillRect(x + 75, 194, 65, 60);
    g.lineStyle(2, 0x5e6b73, 0.6);
    for (let y = 244; y < 600; y += 44) {
      g.lineBetween(x - 180, y, x + 140, y);
      for (let xx = x - 160; xx < x + 140; xx += 74)
        g.lineBetween(xx, y, xx, y + 44);
    }
    g.fillStyle(0x15283c);
    for (let yy = 305; yy < 500; yy += 100) {
      g.fillRoundedRect(x - 110, yy, 48, 70, { tl: 24, tr: 24, bl: 0, br: 0 });
      g.fillRoundedRect(x + 25, yy, 48, 70, { tl: 24, tr: 24, bl: 0, br: 0 });
    }
    g.fillStyle(0x66734c);
    for (let i = 0; i < 12; i++) g.fillEllipse(x - 170 + i * 28, 231, 36, 10);
    this.add
      .text(x - 20, 218, "THE LAST WATCH", {
        fontFamily: "Georgia",
        fontSize: 13,
        color: "#aeb8b6",
      })
      .setOrigin(0.5)
      .setDepth(2);
    const statue = this.add.graphics().setDepth(2);
    statue.fillStyle(0x485662);
    statue.fillRect(x + 250, 550, 65, 52);
    statue.fillRoundedRect(x + 260, 476, 46, 76, 7);
    statue.fillTriangle(x + 249, 549, x + 283, 470, x + 319, 549);
    statue.fillEllipse(x + 283, 460, 42, 49);
    statue.fillTriangle(x + 262, 456, x + 281, 427, x + 304, 456);
    statue.fillStyle(0x263a49);
    statue.fillEllipse(x + 283, 462, 26, 29);
    statue.fillStyle(0x80918f);
    statue.fillRect(x + 276, 457, 4, 2);
    statue.fillRect(x + 287, 457, 4, 2);
    statue.lineStyle(2, 0x6d7b7d);
    statue.lineBetween(x + 269, 488, x + 280, 520);
    statue.lineBetween(x + 297, 488, x + 286, 520);
    statue.lineBetween(x + 263, 562, x + 304, 562);
    statue.lineStyle(3, 0x344950);
    statue.lineBetween(x + 283, 506, x + 283, 546);
    statue.fillStyle(0x6b7952);
    statue.fillEllipse(x + 255, 552, 25, 7);
  }
  lantern(x, y) {
    const g = this.add.graphics().setDepth(4);
    g.lineStyle(4, 0x392e30);
    g.lineBetween(x - 22, y - 65, x - 22, y + 170);
    g.lineBetween(x - 23, y - 64, x + 13, y - 64);
    g.lineStyle(2, 0x433936);
    g.lineBetween(x, y - 64, x, y - 13);
    g.fillStyle(0x5e422e);
    g.fillTriangle(x - 13, y - 10, x, y - 20, x + 13, y - 10);
    g.fillStyle(0xe8b65d);
    g.fillRect(x - 9, y - 10, 18, 25);
    g.lineStyle(3, 0x62462d);
    g.strokeRect(x - 11, y - 11, 22, 27);
    g.lineBetween(x, y - 10, x, y + 15);
    const glow = this.add
      .image(x, y + 3, "glow")
      .setScale(1.25)
      .setDepth(4)
      .setAlpha(0.58);
    this.lights.push(glow);
  }
  start() {
    this.playing = true;
    this.paused = false;
    this.physics.resume();
    this.player.setVelocity(0);
    this.keys && Object.values(this.keys).forEach((k) => k.reset());
  }
  setPaused(value) {
    this.paused = value;
    if (value) {
      this.physics.pause();
      this.player.setAccelerationX(0);
      this.player.setVelocityX(0);
      this.player.play("idle", true);
      Object.values(this.keys).forEach((k) => k.reset());
    } else if (this.playing && !this.victorious) this.physics.resume();
  }
  respawnCoins() {
    this.wallet = 0;
    this.ui.wallet(0);
    for (const coin of this.coinSprites) {
      coin.enableBody(false, coin.x, coin.baseY, true, true);
      coin.setAlpha(1);
    }
  }
  spark(x, y) {
    if (this.reduced) return;
    for (let i = 0; i < 5; i++) {
      const p = this.add.image(x, y, "mote").setTint(0xf0c477).setDepth(8);
      this.tweens.add({
        targets: p,
        x: x + Math.cos(i * 1.3) * 24,
        y: y - 24 + Math.sin(i * 1.3) * 16,
        alpha: 0,
        duration: 420,
        onComplete: () => p.destroy(),
      });
    }
  }
  openVault() {
    if (this.victorious) return;
    this.victorious = true;
    this.physics.pause();
    this.guardian.play("goblin-victory");
    this.ui.sound.play("vault");
    this.tweens.add({ targets: this.door, alpha: 0, duration: 1500 });
    this.tweens.add({
      targets: this.cameras.main,
      scrollX: 0,
      duration: 1200,
      ease: "Sine.easeInOut",
    });
    this.time.delayedCall(1500, () => this.ui.victory());
  }
  update(time, delta) {
    const t = time / 1000;
    if (!this.reduced) {
      this.sway?.forEach(
        (o, i) => (o.rotation = Math.sin(t * 0.4 + i) * 0.005),
      );
      this.lights?.forEach(
        (o, i) => (o.alpha = 0.52 + Math.sin(t * 3.1 + i) * 0.07),
      );
      this.motes?.forEach((o, i) => {
        o.x = ((i * 421 + t * (5 + (i % 7))) % 1350) - 35;
        o.y = 140 + ((i * 137) % 460) + Math.sin(t * 0.4 + i) * 20;
      });
      if (this.mist) this.mist.x = Math.sin(t * 0.07) * 90;
    }
    if (this.water) {
      const g = this.water;
      g.clear();
      g.fillStyle(0x8fbdcf, 0.17);
      g.fillRect(this.waterX, 350, 78, 235);
      g.lineStyle(2, 0xb9e0e6, 0.22);
      for (let i = 0; i < 12; i++) {
        let y = 350 + ((i * 23 + t * 65) % 230);
        g.lineBetween(
          this.waterX + 8 + (i % 4) * 17,
          y,
          this.waterX + 8 + (i % 4) * 17,
          y + 25,
        );
      }
      g.lineStyle(2, 0xa8c9d0, 0.15);
      for (let i = 0; i < 4; i++)
        g.strokeEllipse(
          this.waterX + 40,
          588 + i * 6,
          70 + ((t * 18 + i * 20) % 100),
          8,
        );
    }
    if (this.distantWater) {
      const g = this.distantWater;
      g.clear();
      // Shimmer follows the waterfall inside the distant vista at its own depth.
      g.lineStyle(1.5, 0xd1ebef, 0.19);
      for (let i = 0; i < (this.reduced ? 4 : 12); i++) {
        const p = (i / 12 + t * 0.19) % 1;
        const x = 1320 - p * 45 + (i % 3) * 8;
        const y = 355 + p * 126;
        g.lineBetween(x, y, x - 3, y + 12);
      }
      g.lineStyle(1, 0xc7e1e9, 0.13);
      for (let i = 0; i < 5; i++) {
        const x = 1070 + i * 90 + Math.sin(t * 0.3 + i) * 8;
        g.lineBetween(
          x,
          512 + i * 6,
          x + 20 + Math.sin(t + i) * 8,
          512 + i * 6,
        );
      }
    }
    this.coinSprites?.forEach((c, i) => {
      if (c.active) {
        c.y = c.baseY + Math.sin(t * 2.4 + i) * 4;
        c.scaleX = 0.65 * (0.8 + Math.sin(t * 2 + i) * 0.2);
      }
    });
    if (!this.playing || this.paused || this.victorious) return;
    const body = this.player.body,
      grounded = body.blocked.down || body.touching.down;
    if (grounded) {
      this.lastGround = time;
      if (!this.wasGrounded) {
        this.landUntil = time + 130;
        this.ui.sound.play("land");
      }
    }
    this.wasGrounded = grounded;
    const dir =
      (this.keys.right.isDown || this.keys.arrowRight.isDown ? 1 : 0) -
      (this.keys.left.isDown || this.keys.arrowLeft.isDown ? 1 : 0);
    if (dir) {
      this.facing = dir;
      this.player.setAccelerationX(dir * 1750);
    } else this.player.setAccelerationX(0);
    if (time - this.jumpAt < 130 && time - this.lastGround < 110) {
      this.player.setVelocityY(-570);
      this.jumpAt = -1000;
      this.lastGround = -1000;
      this.ui.sound.play("jump");
    }
    let anim = !grounded
      ? body.velocity.y < 0
        ? "jump"
        : "fall"
      : time < this.landUntil
        ? "land"
        : Math.abs(body.velocity.x) > 18
          ? "run"
          : "idle";
    if (this.player.anims.currentAnim?.key !== anim) this.player.play(anim);
    this.player.setFlipX(this.facing < 0);
    const blend = 1 - Math.exp(-delta * 0.004);
    this.look = Phaser.Math.Linear(this.look, this.facing * 105, blend);
    const target = Phaser.Math.Clamp(
      this.player.x - 640 + this.look,
      0,
      WORLD_WIDTH - 1280,
    );
    if (Math.abs(target - this.cameraX) > 12)
      this.cameraX = Phaser.Math.Linear(
        this.cameraX,
        target,
        1 - Math.exp(-delta * 0.005),
      );
    this.cameras.main.scrollX = this.cameraX;
    this.ui.nearGuardian(Math.abs(this.player.x - 292) < 150);
    const region =
      this.player.x < 1300
        ? "THE CASTLE COURTYARD"
        : this.player.x > 12500
          ? "THE ABANDONED WATCHTOWER"
          : "THE ENCHANTED FOREST";
    this.ui.region(region);
    if (this.player.y > 790) {
      this.player.setPosition(480, GROUND_Y - 20).setVelocity(0);
      this.ui.toast("The old road brings you home. Your gold is safe.");
    }
  }
}
