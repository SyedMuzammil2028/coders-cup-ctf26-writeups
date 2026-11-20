import { pathToFileURL } from "node:url";
export async function createFlagProvider(config) {
  if (config.flagMode === "development")
    return { getFlag: async () => "ACM{DEMO_the_guardian_trusts_the_ledger}" };
  if (config.flagMode === "environment")
    return { getFlag: async () => config.flag };
  const adapter = await import(pathToFileURL(config.adapterPath).href);
  if (typeof adapter.getFlag !== "function")
    throw new Error("Flag adapter must export async getFlag(teamId).");
  return {
    async getFlag(teamId) {
      const flag = await adapter.getFlag(teamId);
      if (
        typeof flag !== "string" ||
        !/^ACM\{[^\r\n{}]+\}$/.test(flag) ||
        flag.length > 2048
      )
        throw new Error("Invalid flag provider response.");
      return flag;
    },
  };
}
