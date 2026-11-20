// Organizer integration contract. Do not serve this directory as static files.
// Replace this body with your trusted infrastructure lookup, using teamId
// from the verified server session. Credentials stay server-side.
export async function getFlag(teamId) {
  throw new Error(
    "Connect the trusted competition flag provider before deployment.",
  );
}
