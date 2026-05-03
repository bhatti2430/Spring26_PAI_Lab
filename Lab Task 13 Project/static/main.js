const applyBtn = document.getElementById('applyBtn');
const backgroundSelect = document.getElementById('background');
const statusCard = document.getElementById('statusCard');
const videoStream = document.getElementById('videoStream');

const showStatus = (title, message, success = true) => {
  statusCard.innerHTML = `<strong>${title}</strong><p>${message}</p>`;
  statusCard.style.borderColor = success ? 'rgba(34, 197, 94, 0.25)' : 'rgba(239, 68, 68, 0.4)';
};

const updateStream = () => {
  videoStream.src = '/video_feed?ts=' + new Date().getTime();
};

window.addEventListener('load', () => {
  updateStream();
  setInterval(updateStream, 250);
});

applyBtn.addEventListener('click', async () => {
  const index = backgroundSelect.value;
  showStatus('Applying background…', 'Sending your choice to the backend, please wait.');

  try {
    const response = await fetch(`/api/set_background?index=${encodeURIComponent(index)}`);
    const data = await response.json();

    if (!response.ok || !data.success) {
      showStatus('Update failed', data.error || 'Could not update the background.', false);
      return;
    }

    showStatus('Background updated', `Now using "${data.background}". The stream will update automatically.`);
    updateStream();
  } catch (error) {
    showStatus('Connection error', 'Unable to reach the Flask backend. Make sure the server is running.', false);
  }
});
