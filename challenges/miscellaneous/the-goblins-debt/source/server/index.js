import { readConfig } from "./config.js";
import { createApp } from "./app.js";
const config = readConfig();
const { app, store } = await createApp(config);
const server = app.listen(config.port, config.host, () =>
  console.log(
    `The Goblin’s Debt: http://${config.host}:${config.port}${config.basePath}/ (${config.authMode})`,
  ),
);
for (const signal of ["SIGINT", "SIGTERM"])
  process.on(signal, () =>
    server.close(() => {
      store.close();
      process.exit(0);
    }),
  );
