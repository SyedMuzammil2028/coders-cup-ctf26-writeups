'use strict';
const seal = document.querySelector('#seal');
const question = document.querySelector('#question');
const form = document.querySelector('#question-form');
const answer = document.querySelector('#answer');
const error = document.querySelector('#answer-error');
const transmission = document.querySelector('#transmission');
const output = document.querySelector('#ciphertext');
const copy = document.querySelector('#copy');
const status = document.querySelector('#copy-status');
let ciphertext = '';
let unlocking = false;
let opener = seal;
let copyTimer;
function openQuestion(event) {
  if (unlocking) return;
  opener = event.currentTarget;
  error.textContent = '';
  answer.removeAttribute('aria-invalid');
  question.showModal();
  answer.focus();
}
seal.addEventListener('click', openQuestion);
document.querySelector('#open-seal').addEventListener('click', openQuestion);
document.querySelector('#close-question').addEventListener('click', () => question.close());
question.addEventListener('click', event => {
  const rect = question.getBoundingClientRect();
  if (!unlocking && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) question.close();
});
question.addEventListener('cancel', event => { if (unlocking) event.preventDefault(); });
question.addEventListener('close', () => { if (!unlocking) opener.focus(); });
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (unlocking) return;
  if (answer.value.trim() !== '4') {
    error.textContent = 'The seal remains unbroken. Try again.';
    answer.setAttribute('aria-invalid', 'true');
    answer.focus();
    return;
  }
  unlocking = true;
  answer.removeAttribute('aria-invalid');
  error.textContent = '';
  question.classList.add('accepted');
  document.querySelector('#unlock').disabled = true;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  await new Promise(resolve => setTimeout(resolve, reduced ? 0 : 180));
  question.close();
  document.querySelector('#vault').classList.add('unsealing');
  const loading = loadCiphertext();
  await new Promise(resolve => setTimeout(resolve, reduced ? 0 : 780));
  document.querySelector('#vault').hidden = true;
  transmission.hidden = false;
  document.querySelector('#transmission-title').focus({preventScroll:true});
  await loading;
});
async function loadCiphertext() {
  try {
    const response = await fetch('ciphertext.json', {cache:'no-store'});
    if (!response.ok) throw new Error('Unavailable');
    const data = await response.json();
    if (typeof data.ciphertext !== 'string' || !/^[01]{8}( [01]{8})*$/.test(data.ciphertext)) throw new Error('Invalid transmission');
    ciphertext = data.ciphertext;
    output.textContent = ciphertext;
    document.querySelector('#byte-count').textContent = `${ciphertext.split(' ').length} BYTES · BINARY`;
    copy.disabled = false;
  } catch {
    output.textContent = 'The transmission could not be retrieved. Reload to try again. If this continues, contact the competition organizers.';
    status.textContent = 'Archive temporarily unavailable.';
  }
}
copy.addEventListener('click', async () => {
  clearTimeout(copyTimer);
  try {
    if (!navigator.clipboard || !window.isSecureContext) throw new Error('Manual copy needed');
    await navigator.clipboard.writeText(ciphertext);
    status.textContent = 'Copied';
    copyTimer = setTimeout(() => { status.textContent = 'Preserved exactly as recovered.'; }, 2500);
  } catch {
    const range = document.createRange();
    range.selectNodeContents(output);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    output.focus();
    status.textContent = /Mac|iPhone|iPad/.test(navigator.userAgent) ? 'Text selected. Press ⌘C, or touch and hold to copy.' : 'Text selected. Press Ctrl+C, or touch and hold to copy.';
  }
});
