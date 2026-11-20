import express from "express";
import { resolve, join } from "node:path";
import { existsSync } from "node:fs";
import { ProgressStore } from "./services/progressStore.js";
import { createFlagProvider } from "./services/flagProvider.js";
import { teamContext, launchHandler } from "./services/teamContext.js";
export async function createApp(config) {
  const app = express(),
    router = express.Router(),
    store = new ProgressStore(config.databasePath);
  let flags;
  try {
    flags = await createFlagProvider(config);
  } catch (e) {
    store.close();
    throw e;
  }
  app.disable("x-powered-by");
  // The bare-prefix redirect must not also match the trailing-slash index.
  app.enable("strict routing");
  app.use((req, res, next) => {
    res.set({
      "X-Content-Type-Options": "nosniff",
      "Referrer-Policy": "no-referrer",
      "X-Frame-Options": "DENY",
      "Content-Security-Policy":
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; font-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
    });
    next();
  });
  router.get("/health", (_, res) => res.json({ ok: true }));
  if (config.authMode === "shared")
    router.get("/launch", launchHandler(config, store));
  router.use(
    "/api",
    (req, res, next) => {
      res.set("Cache-Control", "no-store");
      if (req.method === "POST") {
        if (req.headers["sec-fetch-site"] === "cross-site")
          return res.status(403).json({ error: "Same-origin requests only." });
        if (
          req.headers.origin &&
          req.headers.origin !==
            (config.origin || `${req.protocol}://${req.get("host")}`)
        )
          return res.status(403).json({ error: "Same-origin requests only." });
        if (!req.is("application/json"))
          return res.status(415).json({ error: "Send application/json." });
      }
      next();
    },
    teamContext(config),
    express.json({ limit: "1kb", strict: true }),
  );
  router.get("/api/progress", (req, res) =>
    res.json(store.progress(req.teamId)),
  );
  router.post("/api/ledger/deposit", (req, res) => {
    const coins = req.body?.coins;
    if (
      !req.body ||
      Object.keys(req.body).length !== 1 ||
      !Number.isInteger(coins) ||
      coins < 1 ||
      coins > 23
    )
      return res
        .status(400)
        .json({ error: "coins must be an integer between 1 and 23." });
    // INTENTIONAL CTF WEAKNESS: the ledger trusts this client report. Never add trip verification here.
    res.json(store.deposit(req.teamId, coins));
  });
  router.get("/api/reward", async (req, res) => {
    if (!store.progress(req.teamId).unlocked)
      return res.status(403).json({
        error: "The vault is sealed. The guardian requires 120 coins.",
      });
    try {
      res.json({ flag: Buffer.from(await flags.getFlag(req.teamId), "utf8").toString("base64") });
    } catch {
      console.error("Flag provider failed; saved progress retained.");
      res.status(503).json({
        error:
          "The flag provider is unavailable. Your debt is paid; please retry.",
      });
    }
  });
  router.use("/api", (_, res) =>
    res.status(404).json({ error: "Unknown API endpoint." }),
  );
  const publicRoot = resolve("dist");
  if (existsSync(publicRoot)) {
    router.use(
      express.static(publicRoot, {
        dotfiles: "deny",
        index: false,
        redirect: false,
        maxAge: config.production ? "1h" : 0,
      }),
    );
    router.get("/", (_, res) =>
      res
        .set("Cache-Control", "no-cache")
        .sendFile(join(publicRoot, "index.html")),
    );
  } else
    router.get("/", (_, res) =>
      res
        .status(503)
        .type("text")
        .send("Build the client first: npm run build"),
    );
  if (config.basePath)
    app.get(config.basePath, (_, res) =>
      res.redirect(308, `${config.basePath}/`),
    );
  app.use(config.basePath || "/", router);
  app.use((err, req, res, next) => {
    if (res.headersSent) return next(err);
    const status =
      err.type === "entity.too.large"
        ? 413
        : err instanceof SyntaxError
          ? 400
          : 500;
    if (status === 500) console.error("Request failed:", err.code || err.name);
    res.status(status).json({
      error:
        status === 413
          ? "Request too large."
          : status === 400
            ? "Invalid JSON."
            : "The ledger is temporarily unavailable.",
    });
  });
  return { app, store };
}
