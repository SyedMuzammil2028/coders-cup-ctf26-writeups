export const WORLD_WIDTH = 14200;
export const GROUND_Y = 602;
export const SPEED = 250;
// Broad paths keep the challenge forgiving. Optional ledges are always < jump apex.
export const platforms = [
  ...Array.from({ length: 11 }, (_, i) => ({
    x: 1510 + i * 1150,
    y: i % 3 === 2 ? 470 : 500,
    width: 245,
  })),
  { x: 13590, y: 470, width: 245 },
];
export const coinPositions = Array.from({ length: 23 }, (_, i) => {
  const x = 1020 + i * 575;
  const platform = platforms.find(
    (p) => x >= p.x - 25 && x <= p.x + p.width + 25,
  );
  return { x, y: platform ? platform.y - 32 : GROUND_Y - 37 };
});
export const hazards = [2820, 5220, 8620, 11120];
