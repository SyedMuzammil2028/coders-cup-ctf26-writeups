import { createHmac, timingSafeEqual } from "node:crypto";
export function signToken(payload, secret) {
  const encoded = Buffer.from(JSON.stringify(payload)).toString("base64url");
  return `${encoded}.${createHmac("sha256", secret).update(encoded).digest("base64url")}`;
}
export function verifyToken(token, secret) {
  if (typeof token !== "string" || token.length > 4096) return null;
  const parts = token.split(".");
  if (parts.length !== 2) return null;
  const signature = createHmac("sha256", secret).update(parts[0]).digest(),
    received = Buffer.from(parts[1], "base64url");
  if (
    signature.length !== received.length ||
    !timingSafeEqual(signature, received)
  )
    return null;
  try {
    const p = JSON.parse(Buffer.from(parts[0], "base64url").toString());
    if (
      !Number.isSafeInteger(p.exp) ||
      p.exp <= Date.now() / 1000 ||
      typeof p.teamId !== "string" ||
      !p.teamId.length ||
      p.teamId.length > 128
    )
      return null;
    return p;
  } catch {
    return null;
  }
}
function cookie(req, name) {
  const match = (req.headers.cookie || "")
    .split(";")
    .map((s) => s.trim())
    .find((s) => s.startsWith(name + "="));
  return match?.slice(name.length + 1);
}
export function teamContext(config) {
  return (req, res, next) => {
    if (config.authMode === "development") req.teamId = "local-development";
    else if (config.authMode === "instance") req.teamId = config.instanceId;
    else {
      const p = verifyToken(
        cookie(req, "goblin_session"),
        config.sessionSecret,
      );
      if (!p || p.aud !== "goblins-debt-session")
        return res
          .status(401)
          .json({
            error:
              "Open this challenge through your team’s authenticated competition launch link.",
          });
      req.teamId = p.teamId;
    }
    next();
  };
}
export function launchHandler(config, store) {
  return (req, res) => {
    const p = verifyToken(req.query.token, config.launchSecret),
      now = Math.floor(Date.now() / 1000);
    if (
      !p ||
      p.aud !== "goblins-debt-launch" ||
      p.exp > now + 300 ||
      typeof p.nonce !== "string" ||
      !/^[a-zA-Z0-9_-]{16,128}$/.test(p.nonce) ||
      !store.consumeNonce(p.nonce, p.exp)
    )
      return res
        .status(401)
        .type("text")
        .send(
          "Invalid, expired, or already used launch link. Request a new link from the competition platform.",
        );
    res.cookie(
      "goblin_session",
      signToken(
        { teamId: p.teamId, exp: now + 43200, aud: "goblins-debt-session" },
        config.sessionSecret,
      ),
      {
        httpOnly: true,
        secure: config.production,
        sameSite: "strict",
        path: config.basePath || "/",
        maxAge: 43200000,
      },
    );
    res.redirect(303, `${config.basePath}/`);
  };
}
