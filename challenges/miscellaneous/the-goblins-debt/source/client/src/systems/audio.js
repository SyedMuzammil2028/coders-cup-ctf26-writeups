export class Sound {
  enabled = false;
  unlock() {
    try {
      this.context ??= new AudioContext();
      if (this.context.state === "suspended")
        this.context.resume().catch(() => {});
    } catch {}
  }
  play(kind) {
    if (!this.enabled) return;
    this.unlock();
    if (!this.context) return;
    const notes = {
      coin: [880, 1320],
      jump: [240, 400],
      land: [100, 75],
      talk: [290, 360],
      deposit: [440, 660, 880],
      vault: [220, 330, 440, 660],
    }[kind] || [440];
    notes.forEach((freq, i) => {
      const t = this.context.currentTime + i * 0.075,
        o = this.context.createOscillator(),
        g = this.context.createGain();
      o.type = "sine";
      o.frequency.setValueAtTime(freq, t);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.035, t + 0.012);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.23);
      o.connect(g).connect(this.context.destination);
      o.start(t);
      o.stop(t + 0.25);
    });
  }
}
