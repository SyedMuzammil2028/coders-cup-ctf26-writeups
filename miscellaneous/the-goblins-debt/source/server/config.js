import { resolve } from "node:path";
export function readConfig(env = process.env) {
  const production = env.NODE_ENV === "production",
    authMode = env.AUTH_MODE,
    flagMode = env.FLAG_MODE;
  if (!["development", "instance", "shared"].includes(authMode))
    throw new Error(
      "Set AUTH_MODE explicitly: development, instance, or shared.",
    );
  if (!["development", "environment", "adapter"].includes(flagMode))
    throw new Error(
      "Set FLAG_MODE explicitly: development, environment, or adapter.",
    );
  if (production && (authMode === "development" || flagMode === "development"))
    throw new Error(
      "Development identity and flags are forbidden in production.",
    );
  if (authMode === "instance" && !env.INSTANCE_ID)
    throw new Error("INSTANCE_ID is required.");
  if (flagMode === "environment" && authMode !== "instance")
    throw new Error("Environment flags require an isolated instance identity.");
  if (flagMode === "development" && authMode !== "development")
    throw new Error("Demo flags require development authentication.");
  if (
    authMode === "shared" &&
    (flagMode !== "adapter" ||
      !env.PUBLIC_ORIGIN ||
      !env.SESSION_SECRET ||
      env.SESSION_SECRET.length < 32 ||
      !env.LAUNCH_SECRET ||
      env.LAUNCH_SECRET.length < 32 ||
      env.SESSION_SECRET === env.LAUNCH_SECRET)
  )
    throw new Error(
      "Shared mode requires an adapter, PUBLIC_ORIGIN, and two different secrets of at least 32 characters.",
    );
  if (flagMode === "environment" && !/^ACM\{[^\r\n{}]+\}$/.test(env.FLAG || ""))
    throw new Error("FLAG must be a nonempty ACM{...} flag.");
  if (flagMode === "adapter" && !env.FLAG_ADAPTER_PATH)
    throw new Error("FLAG_ADAPTER_PATH is required.");
  const basePath = (env.BASE_PATH || "").replace(/\/$/, "");
  if (basePath && !/^\/[a-zA-Z0-9_/-]+$/.test(basePath))
    throw new Error(
      "BASE_PATH must be a simple absolute URL path without a trailing slash.",
    );
  const origin = env.PUBLIC_ORIGIN ? new URL(env.PUBLIC_ORIGIN).origin : null;
  if (production && authMode === "shared" && !origin.startsWith("https://"))
    throw new Error(
      "Production shared sessions require an HTTPS PUBLIC_ORIGIN.",
    );
  return {
    production,
    authMode,
    flagMode,
    basePath,
    origin,
    sessionSecret: env.SESSION_SECRET,
    launchSecret: env.LAUNCH_SECRET,
    instanceId: env.INSTANCE_ID,
    flag: env.FLAG,
    adapterPath: env.FLAG_ADAPTER_PATH ? resolve(env.FLAG_ADAPTER_PATH) : null,
    databasePath: env.DATABASE_PATH || "./data/progress.sqlite",
    port: Number(env.PORT || 3000),
    host: env.HOST || "127.0.0.1",
  };
}
