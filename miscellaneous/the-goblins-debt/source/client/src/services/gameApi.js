const apiRoot = new URL("api/", document.baseURI);
async function request(path, options = {}) {
  const response = await fetch(new URL(path, apiRoot), {
    credentials: "same-origin",
    cache: "no-store",
    ...options,
  });
  const data = await response
    .json()
    .catch(() => ({ error: "The guardian sent an unreadable reply." }));
  if (!response.ok)
    throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
export const gameApi = {
  progress: () => request("progress"),
  deposit: (coins) =>
    request("ledger/deposit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ coins }),
    }),
  reward: () => request("reward"),
};
