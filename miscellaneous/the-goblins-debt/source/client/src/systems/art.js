// Original runtime artwork, articulated from the supplied character designs.
// Canvas paths are baked once into compact textures; no per-frame path rendering.
const ink = "#302a2e";
function shape(c, fill, points, stroke = ink, width = 2) {
  c.beginPath();
  points(c);
  c.fillStyle = fill;
  c.fill();
  if (stroke) {
    c.strokeStyle = stroke;
    c.lineWidth = width;
    c.lineJoin = "round";
    c.stroke();
  }
}
function ellipse(c, x, y, rx, ry, fill, stroke = null) {
  shape(c, fill, (p) => p.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2), stroke);
}
function path(c, fill, d, stroke = ink, w = 2) {
  shape(
    c,
    fill,
    (p) => {
      for (const s of d) {
        const [op, ...args] = s;
        p[op](...args);
      }
    },
    stroke,
    w,
  );
}
function limb(c, x, y, angle, length, width, color, boot = false) {
  c.save();
  c.translate(x, y);
  c.rotate(angle);
  c.fillStyle = color;
  c.strokeStyle = ink;
  c.lineWidth = 2;
  c.beginPath();
  c.roundRect(-width / 2, 0, width, length, 4);
  c.fill();
  c.stroke();
  if (boot) {
    c.fillStyle = "#53352f";
    c.beginPath();
    c.roundRect(-width / 2 - 2, length - 10, width + 9, 13, 3);
    c.fill();
    c.stroke();
    c.fillStyle = "#79503d";
    c.fillRect(-width / 2 - 2, length - 13, width + 3, 5);
  }
  c.restore();
}
function hero(c, phase, state) {
  c.save();
  c.translate(64, 118);
  const run = state === "run",
    air = state === "jump" || state === "fall";
  const swing = run
    ? Math.sin(phase) * 0.75
    : state === "jump"
      ? phase < Math.PI
        ? 0.5
        : 0.8
      : state === "fall"
        ? 0.22
        : Math.sin(phase) * 0.035;
  const bob = run ? -Math.abs(Math.cos(phase)) * 2 : Math.sin(phase) * 0.65;
  c.translate(0, bob);
  if (state === "land") c.scale(1, 0.92 + (0.08 * phase) / ((Math.PI * 4) / 3));
  if (!air) ellipse(c, 0, 2, 22, 4, "#10192344");
  const tuck = state === "jump" ? (phase < Math.PI ? 27 : 21) : 30;
  limb(c, -9, -32, swing, tuck, 12, "#49322e", true);
  limb(
    c,
    9,
    -32,
    -swing,
    state === "jump" ? tuck - 2 : tuck,
    12,
    "#634031",
    true,
  );
  // Cloak has its own trailing hem, with fixed shoulders.
  const trail = run
    ? -9
    : state === "fall"
      ? -19
      : air
        ? -8
        : Math.sin(phase) * 2;
  path(c, "#762c32", [
    ["moveTo", -20, -71],
    ["quadraticCurveTo", -35 + trail, -50, -31 + trail, -27],
    ["lineTo", -12, -34],
    ["lineTo", 13, -25],
    ["lineTo", 28, -35],
    ["lineTo", 18, -72],
    ["closePath"],
  ]);
  path(c, "#e8d8b2", [
    ["moveTo", -15, -65],
    ["lineTo", 13, -65],
    ["lineTo", 19, -31],
    ["lineTo", -20, -31],
    ["closePath"],
  ]);
  const leftArm = state === "fall" ? 0.7 : -swing * 0.65;
  const rightArm = state === "fall" ? -0.7 : swing * 0.65;
  limb(c, -20, -63, leftArm, 27, 10, "#99664b");
  limb(c, 19, -63, rightArm, 27, 10, "#b28360");
  ellipse(
    c,
    -20 - Math.sin(leftArm) * 27,
    -63 + Math.cos(leftArm) * 27,
    7,
    8,
    "#52332c",
  );
  ellipse(
    c,
    19 - Math.sin(rightArm) * 27,
    -63 + Math.cos(rightArm) * 27,
    7,
    8,
    "#52332c",
  );
  path(c, "#ad433e", [
    ["moveTo", -21, -74],
    ["quadraticCurveTo", -22, -57, -30 + trail, -39],
    ["lineTo", -17, -45],
    ["lineTo", -10, -39],
    ["lineTo", 6, -62],
    ["lineTo", 24, -41],
    ["lineTo", 27, -51],
    ["lineTo", 20, -77],
    ["closePath"],
  ]);
  path(
    c,
    "#e2b569",
    [
      ["moveTo", -30 + trail, -39],
      ["lineTo", -17, -45],
      ["lineTo", -10, -39],
      ["lineTo", 5, -59],
      ["lineTo", 24, -41],
      ["lineTo", 25, -45],
      ["lineTo", 5, -65],
      ["lineTo", -12, -45],
      ["lineTo", -18, -50],
      ["lineTo", -29 + trail, -44],
      ["closePath"],
    ],
    null,
  );
  c.fillStyle = "#52382d";
  c.fillRect(-18, -36, 36, 6);
  c.strokeStyle = "#d5ab60";
  c.lineWidth = 3;
  c.strokeRect(-1, -37, 10, 8);
  path(
    c,
    "#5f3a2e",
    [
      ["moveTo", 7, -66],
      ["lineTo", 12, -63],
      ["lineTo", -13, -32],
      ["lineTo", -17, -35],
      ["closePath"],
    ],
    null,
  );
  c.fillStyle = "#83513a";
  c.strokeStyle = ink;
  c.lineWidth = 2;
  c.beginPath();
  c.roundRect(-23, -35, 15, 19, 3);
  c.fill();
  c.stroke();
  ellipse(c, -16, -30, 2, 2, "#c09359");
  // Hood, face and hair retain the canonical red hood and youthful silhouette.
  path(c, "#a43e39", [
    ["moveTo", -27, -69],
    ["quadraticCurveTo", -39, -86, -27, -107],
    ["quadraticCurveTo", -13, -124, 8, -116],
    ["quadraticCurveTo", 30, -107, 32, -79],
    ["quadraticCurveTo", 17, -65, -27, -69],
    ["closePath"],
  ]);
  path(
    c,
    "#722b2b",
    [
      ["moveTo", -26, -73],
      ["quadraticCurveTo", -28, -96, -9, -111],
      ["quadraticCurveTo", 21, -112, 27, -79],
      ["quadraticCurveTo", 10, -66, -26, -73],
      ["closePath"],
    ],
    null,
  );
  ellipse(c, 0, -87, 20, 22, "#edc394", ink);
  path(c, "#53382f", [
    ["moveTo", -22, -88],
    ["lineTo", -24, -102],
    ["lineTo", -32, -108],
    ["lineTo", -15, -107],
    ["quadraticCurveTo", -9, -119, 1, -110],
    ["lineTo", 9, -113],
    ["lineTo", 23, -96],
    ["lineTo", 15, -102],
    ["lineTo", 11, -83],
    ["lineTo", 7, -101],
    ["quadraticCurveTo", -8, -86, -20, -86],
    ["lineTo", -16, -96],
    ["closePath"],
  ]);
  const blink = state === "idle" && phase > 4.8;
  ellipse(c, -5, -88, 2.4, blink ? 0.8 : 4.6, "#30252b");
  ellipse(c, 11, -88, 2.3, blink ? 0.8 : 4.6, "#30252b");
  path(c, "#c15344", [
    ["moveTo", -26, -70],
    ["quadraticCurveTo", 0, -59, 23, -72],
    ["lineTo", 18, -64],
    ["quadraticCurveTo", 0, -54, -24, -64],
    ["closePath"],
  ]);
  ellipse(c, 15, -63, 5.2, 5.8, "#e1b04e", "#714d2a");
  ellipse(c, 14, -65, 1.6, 1.8, "#ffe0a1");
  c.restore();
}
function goblin(c, phase, state) {
  c.save();
  c.translate(96, 176);
  const breath = Math.sin(phase) * 1.2;
  c.translate(0, breath);
  ellipse(c, 0, 0, 45, 6, "#07111b77");
  limb(c, -20, -40, -0.08, 38, 19, "#32282a", true);
  limb(c, 19, -40, 0.06, 38, 19, "#32282a", true);
  path(c, "#632733", [
    ["moveTo", -37, -109],
    ["lineTo", 36, -109],
    ["lineTo", 49, -30],
    ["lineTo", 21, -38],
    ["lineTo", 15, -25],
    ["lineTo", 2, -58],
    ["lineTo", -18, -25],
    ["lineTo", -28, -38],
    ["lineTo", -49, -30],
    ["closePath"],
  ]);
  path(
    c,
    "#b88748",
    [
      ["moveTo", -36, -110],
      ["lineTo", -44, -120],
      ["lineTo", -15, -110],
      ["lineTo", 0, -88],
      ["lineTo", 18, -110],
      ["lineTo", 44, -121],
      ["lineTo", 34, -106],
      ["lineTo", 24, -32],
      ["lineTo", 20, -33],
      ["lineTo", 28, -102],
      ["lineTo", 1, -79],
      ["lineTo", -27, -103],
      ["lineTo", -20, -33],
      ["lineTo", -24, -32],
      ["closePath"],
    ],
    null,
  );
  path(c, "#352c2a", [
    ["moveTo", -16, -107],
    ["lineTo", 17, -107],
    ["lineTo", 22, -50],
    ["lineTo", 0, -44],
    ["lineTo", -22, -50],
    ["closePath"],
  ]);
  for (let y = -88; y < -49; y += 16) ellipse(c, 3, y, 3, 3, "#d7a652");
  path(c, "#e4d2ad", [
    ["moveTo", -11, -112],
    ["lineTo", 9, -112],
    ["lineTo", 18, -92],
    ["lineTo", 3, -96],
    ["lineTo", 0, -87],
    ["lineTo", -20, -93],
    ["closePath"],
  ]);
  const gesture =
    state === "idle"
      ? Math.sin(phase) * 0.035
      : state === "victory"
        ? -0.8
        : Math.sin(phase) * 0.22 - 0.4;
  limb(c, -35, -105, 0.25, 37, 22, "#792e3b");
  limb(c, 36, -103, gesture, 39, 22, "#792e3b");
  c.save();
  c.translate(36, -103);
  c.rotate(gesture);
  c.fillStyle = "#c09351";
  c.fillRect(-12, 27, 24, 5);
  ellipse(c, 1, 43, 12, 11, "#8d9850", ink);
  c.strokeStyle = "#5a6638";
  c.lineWidth = 1;
  c.beginPath();
  c.moveTo(0, 44);
  c.lineTo(1, 51);
  c.moveTo(6, 43);
  c.lineTo(7, 49);
  c.stroke();
  c.restore();
  ellipse(c, -45, -66, 11, 11, "#829047", ink);
  path(c, "#8d964b", [
    ["moveTo", -28, -149],
    ["lineTo", -67, -152],
    ["lineTo", -39, -131],
    ["lineTo", -22, -129],
    ["lineTo", 25, -130],
    ["lineTo", 65, -152],
    ["lineTo", 29, -147],
    ["closePath"],
  ]);
  path(
    c,
    "#67713b",
    [
      ["moveTo", -57, -149],
      ["lineTo", -31, -143],
      ["lineTo", -34, -133],
      ["closePath"],
    ],
    null,
  );
  path(
    c,
    "#b1ae5b",
    [
      ["moveTo", 32, -142],
      ["lineTo", 56, -149],
      ["lineTo", 37, -134],
      ["closePath"],
    ],
    null,
  );
  ellipse(c, 0, -139, 36, 29, "#969e50", ink);
  path(
    c,
    "#ded0a8",
    [
      ["moveTo", -30, -157],
      ["quadraticCurveTo", -28, -177, -11, -181],
      ["lineTo", -16, -188],
      ["quadraticCurveTo", 0, -186, 8, -177],
      ["lineTo", 6, -184],
      ["quadraticCurveTo", 28, -180, 31, -162],
      ["quadraticCurveTo", 11, -172, -7, -158],
      ["closePath"],
    ],
    null,
  );
  path(
    c,
    "#ddd2ac",
    [
      ["moveTo", -26, -148],
      ["quadraticCurveTo", -14, -137, -4, -150],
      ["quadraticCurveTo", -17, -150, -26, -148],
    ],
    ink,
    1.5,
  );
  const blink = state === "idle" && phase > 4.8;
  ellipse(c, -15, -147, 3, blink ? 0.7 : 2, "#181f22");
  ellipse(c, 19, -147, 3, blink ? 0.7 : 3, "#182025");
  path(
    c,
    "#a3aa53",
    [
      ["moveTo", 1, -148],
      ["quadraticCurveTo", 10, -155, 24, -134],
      ["lineTo", 4, -135],
      ["closePath"],
    ],
    null,
  );
  c.strokeStyle = "#443b2d";
  c.lineWidth = 3;
  c.beginPath();
  c.moveTo(-28, -156);
  c.lineTo(-8, -151);
  c.moveTo(10, -153);
  c.lineTo(28, -157);
  c.stroke();
  c.strokeStyle = "#e0b453";
  c.lineWidth = 3;
  c.beginPath();
  c.ellipse(20, -147, 11, 12, 0, 0, Math.PI * 2);
  c.stroke();
  c.lineWidth = 1;
  c.beginPath();
  c.moveTo(30, -143);
  c.quadraticCurveTo(43, -110, 25, -105);
  c.stroke();
  c.strokeStyle = "#41412d";
  c.lineWidth = 2;
  c.beginPath();
  c.moveTo(-18, -128);
  c.quadraticCurveTo(0, -118, 20, -130);
  c.stroke();
  if (state === "talk" && Math.sin(phase) > 0)
    ellipse(c, -1, -124, 6, 2, "#41312b");
  ellipse(c, -43, -128, 4, 6, "#cfa047");
  c.restore();
}
function texture(scene, key, w, h, draw) {
  const tex = scene.textures.createCanvas(key, w, h);
  draw(tex.context);
  tex.refresh();
  return tex;
}
export function makeArt(scene) {
  for (const [state, n] of [
    ["idle", 6],
    ["run", 8],
    ["jump", 2],
    ["fall", 2],
    ["land", 3],
  ]) {
    const tex = texture(scene, `hero-${state}`, 128 * n, 128, (c) => {
      for (let i = 0; i < n; i++) {
        c.save();
        c.translate(i * 128, 0);
        hero(c, (i / n) * Math.PI * 2, state);
        c.restore();
      }
    });
    for (let i = 0; i < n; i++) tex.add(i, 0, i * 128, 0, 128, 128);
    scene.anims.create({
      key: state,
      frames: Array.from({ length: n }, (_, i) => ({
        key: `hero-${state}`,
        frame: i,
      })),
      frameRate:
        state === "run" ? 12 : state === "land" ? 16 : state === "jump" ? 8 : 5,
      repeat: state === "land" || state === "jump" ? 0 : -1,
    });
  }
  for (const state of ["idle", "talk", "deposit", "victory"]) {
    const tex = texture(scene, `goblin-${state}`, 192 * 6, 208, (c) => {
      for (let i = 0; i < 6; i++) {
        c.save();
        c.translate(i * 192, 16);
        goblin(c, (i / 6) * Math.PI * 2, state);
        c.restore();
      }
    });
    for (let i = 0; i < 6; i++) tex.add(i, 0, i * 192, 0, 192, 208);
    scene.anims.create({
      key: `goblin-${state}`,
      frames: Array.from({ length: 6 }, (_, i) => ({
        key: `goblin-${state}`,
        frame: i,
      })),
      frameRate: 6,
      repeat: -1,
    });
  }
  texture(scene, "coin", 40, 40, (c) => {
    ellipse(c, 20, 20, 14, 16, "#8b5c2d", "#5a412b");
    ellipse(c, 20, 19, 11, 14, "#e5b858", "#f4d996");
    ellipse(c, 20, 19, 7, 10, "#c7933e");
    c.fillStyle = "#f6d27b";
    c.font = "bold 18px Georgia";
    c.textAlign = "center";
    c.fillText("◇", 20, 25);
  });
  texture(scene, "glow", 128, 128, (c) => {
    const g = c.createRadialGradient(64, 64, 0, 64, 64, 64);
    g.addColorStop(0, "#ffd58580");
    g.addColorStop(0.2, "#efb85730");
    g.addColorStop(1, "#efb85700");
    c.fillStyle = g;
    c.fillRect(0, 0, 128, 128);
  });
  texture(scene, "mote", 8, 8, (c) => ellipse(c, 4, 4, 2, 2, "#e3d7a1"));
  texture(scene, "stone", 256, 200, (c) => {
    c.fillStyle = "#1b2a39";
    c.fillRect(0, 0, 256, 200);
    for (let row = 0; row < 5; row++)
      for (let col = -1; col < 5; col++) {
        let x = col * 71 + (row % 2) * 32,
          y = row * 40;
        path(
          c,
          ["#354151", "#3d4755", "#293a48", "#384552"][(row + col + 5) % 4],
          [
            ["moveTo", x + 7, y + 3],
            ["lineTo", x + 53, y + 1],
            ["lineTo", x + 67, y + 7],
            ["lineTo", x + 64, y + 29],
            ["lineTo", x + 53, y + 38],
            ["lineTo", x + 10, y + 36],
            ["lineTo", x + 2, y + 27],
            ["lineTo", x + 2, y + 10],
            ["closePath"],
          ],
          "#182633",
          2,
        );
        c.strokeStyle = "#7a827144";
        c.lineWidth = 2;
        c.beginPath();
        c.moveTo(x + 9, y + 7);
        c.lineTo(x + 52, y + 5);
        c.lineTo(x + 61, y + 10);
        c.stroke();
        c.strokeStyle = "#152737";
        c.beginPath();
        c.moveTo(x + 30, y + 39);
        c.lineTo(x + 35, y + 28);
        c.lineTo(x + 31, y + 24);
        c.stroke();
      }
    path(
      c,
      "#768b3d",
      [
        ["moveTo", 0, 0],
        ["lineTo", 256, 0],
        ["lineTo", 256, 8],
        ["lineTo", 230, 6],
        ["lineTo", 224, 18],
        ["lineTo", 213, 10],
        ["lineTo", 196, 9],
        ["lineTo", 191, 21],
        ["lineTo", 181, 8],
        ["lineTo", 133, 10],
        ["lineTo", 120, 16],
        ["lineTo", 109, 8],
        ["lineTo", 64, 9],
        ["lineTo", 56, 26],
        ["lineTo", 45, 12],
        ["lineTo", 0, 10],
        ["closePath"],
      ],
      null,
    );
    c.strokeStyle = "#b7be61";
    c.lineWidth = 3;
    c.beginPath();
    c.moveTo(0, 2);
    c.lineTo(256, 2);
    c.stroke();
  });
  texture(scene, "ledge", 256, 64, (c) => {
    path(
      c,
      "#354253",
      [
        ["moveTo", 0, 0],
        ["lineTo", 256, 0],
        ["lineTo", 247, 35],
        ["lineTo", 209, 40],
        ["lineTo", 182, 60],
        ["lineTo", 136, 48],
        ["lineTo", 97, 62],
        ["lineTo", 63, 40],
        ["lineTo", 14, 33],
        ["closePath"],
      ],
      "#172433",
      3,
    );
    for (let i = 0; i < 5; i++) {
      c.strokeStyle = "#152533";
      c.beginPath();
      c.moveTo(i * 55, 3);
      c.lineTo(i * 55 + 10, 27);
      c.lineTo(i * 55, 42);
      c.stroke();
    }
    path(
      c,
      "#859346",
      [
        ["moveTo", 0, 0],
        ["lineTo", 256, 0],
        ["lineTo", 254, 8],
        ["lineTo", 231, 7],
        ["lineTo", 224, 23],
        ["lineTo", 214, 10],
        ["lineTo", 165, 9],
        ["lineTo", 151, 17],
        ["lineTo", 142, 8],
        ["lineTo", 60, 9],
        ["lineTo", 48, 23],
        ["lineTo", 43, 9],
        ["lineTo", 0, 10],
        ["closePath"],
      ],
      null,
    );
    c.fillStyle = "#b5b967";
    c.fillRect(4, 0, 245, 3);
  });
  for (let variant = 0; variant < 3; variant++)
    texture(scene, `tree-${variant}`, 480, 720, (c) => {
      const dark = variant === 0,
        trunk = dark ? "#152939" : "#29303c",
        leaf = dark ? "#23475a" : variant === 1 ? "#6d2d47" : "#883448";
      path(
        c,
        trunk,
        [
          ["moveTo", 174, 720],
          ["quadraticCurveTo", 239, 480, 202, 315],
          ["quadraticCurveTo", 172, 178, 85, 133],
          ["quadraticCurveTo", 191, 158, 234, 253],
          ["quadraticCurveTo", 256, 120, 327, 53],
          ["quadraticCurveTo", 280, 184, 272, 298],
          ["quadraticCurveTo", 344, 183, 442, 189],
          ["quadraticCurveTo", 330, 235, 277, 374],
          ["quadraticCurveTo", 246, 522, 299, 720],
          ["closePath"],
        ],
        null,
      );
      path(
        c,
        dark ? "#2b4b5a" : "#62413d",
        [
          ["moveTo", 213, 720],
          ["quadraticCurveTo", 255, 491, 239, 364],
          ["lineTo", 249, 276],
          ["quadraticCurveTo", 262, 518, 245, 720],
          ["closePath"],
        ],
        null,
      );
      for (let j = 0; j < 52; j++) {
        let x = 70 + (Math.sin(j * 7.13 + variant) * 0.5 + 0.5) * 340,
          y = 36 + (Math.cos(j * 3.17) * 0.5 + 0.5) * 190;
        ellipse(
          c,
          x,
          y,
          35 + (j % 4) * 10,
          20 + (j % 3) * 7,
          j % 4 === 0 ? (dark ? "#2b5264" : "#ac454b") : leaf,
        );
      }
      for (let j = 0; j < 10; j++) {
        c.strokeStyle = dark ? "#284e57" : "#3e5146";
        c.lineWidth = 2;
        c.beginPath();
        let x = 70 + j * 35;
        c.moveTo(x, 230);
        c.quadraticCurveTo(x - 10, 300, x + 4, 350 + j * 7);
        c.stroke();
        for (let k = 0; k < 5; k++)
          ellipse(
            c,
            x + (k % 2 ? 7 : -7),
            260 + k * 17,
            8,
            4,
            dark ? "#335563" : "#64784b",
          );
      }
    });
  texture(scene, "bush", 256, 96, (c) => {
    for (let i = 0; i < 19; i++) {
      const x = 26 + i * 11,
        y = 55 + Math.sin(i * 5) * 12;
      ellipse(c, x, y, 26, 21, i % 3 ? "#253f43" : "#3e5650");
    }
    for (let i = 0; i < 30; i++) {
      c.strokeStyle = i % 3 ? "#607a48" : "#899151";
      c.lineWidth = 2;
      c.beginPath();
      c.moveTo(15 + i * 7, 96);
      c.quadraticCurveTo(23 + i * 7, 68, 11 + i * 7, 52 + (i % 5) * 6);
      c.stroke();
    }
  });
  texture(scene, "fern", 180, 180, (c) => {
    for (let j = 0; j < 7; j++) {
      const a = -1.2 + j * 0.4;
      c.save();
      c.translate(90, 180);
      c.rotate(a);
      path(
        c,
        "#112b37",
        [
          ["moveTo", 0, 0],
          ["quadraticCurveTo", -18, -60, 0, -140],
          ["quadraticCurveTo", 30, -40, 0, 0],
          ["closePath"],
        ],
        null,
      );
      c.restore();
    }
  });
  texture(scene, "mushroom", 64, 64, (c) => {
    path(
      c,
      "#d6c3a1",
      [
        ["moveTo", 27, 60],
        ["lineTo", 26, 30],
        ["lineTo", 38, 30],
        ["lineTo", 40, 60],
        ["closePath"],
      ],
      null,
    );
    path(
      c,
      "#b34f46",
      [
        ["moveTo", 6, 32],
        ["quadraticCurveTo", 30, -9, 58, 32],
        ["quadraticCurveTo", 32, 43, 6, 32],
        ["closePath"],
      ],
      "#4b3235",
      2,
    );
    for (let i = 0; i < 5; i++)
      ellipse(c, 15 + i * 8, 24 - Math.sin(i) * 7, 3, 2, "#ead4b4");
  });
}
