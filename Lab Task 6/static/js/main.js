document.addEventListener('DOMContentLoaded', function () {
  // Theme Toggle
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;
  
  // Load saved theme or default to light
  const savedTheme = localStorage.getItem('theme') || 'light';
  html.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (themeToggle) {
      themeToggle.innerHTML = theme === 'light' 
        ? '<i class="bi bi-moon-fill"></i>' 
        : '<i class="bi bi-sun-fill"></i>';
      themeToggle.title = theme === 'light' 
        ? 'Switch to dark mode' 
        : 'Switch to light mode';
    }
  }

  // Video Upload Functionality
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('video');
  const previewCard = document.getElementById('preview-card');
  const preview = document.getElementById('preview');
  const uploadBtn = document.getElementById('upload-btn');
  const clearBtn = document.getElementById('clear-btn');
  const progressBar = document.getElementById('upload-progress');
  const statusText = document.getElementById('status-text');

  let selectedFile = null;

  function setStatus(text) { statusText.textContent = text || ''; }

  function enableUpload(enable) {
    uploadBtn.disabled = !enable;
  }

  function clearSelection() {
    selectedFile = null;
    preview.pause();
    preview.removeAttribute('src');
    previewCard.classList.add('d-none');
    fileInput.value = '';
    progressBar.style.width = '0%';
    progressBar.textContent = '0%';
    setStatus('');
    enableUpload(false);
  }

  dropzone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(evt => {
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); });
  });
  ['dragleave', 'drop', 'dragend'].forEach(evt => {
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove('drag-over'); });
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (!dt || !dt.files || !dt.files.length) return;
    handleFile(dt.files[0]);
  });

  fileInput.addEventListener('change', (e) => {
    if (!e.target.files || !e.target.files[0]) return;
    handleFile(e.target.files[0]);
  });

  clearBtn.addEventListener('click', () => clearSelection());

  function handleFile(file) {
    if (!file.type.startsWith('video/')) {
      setStatus('Please select a valid video file.');
      return;
    }

    selectedFile = file;
    const url = URL.createObjectURL(file);
    preview.src = url;
    previewCard.classList.remove('d-none');
    enableUpload(true);
    setStatus(`Selected: ${file.name} (${Math.round(file.size/1024)} KB)`);
  }

  uploadBtn.addEventListener('click', () => {
    if (!selectedFile) return;
    uploadFile(selectedFile);
  });

  function uploadFile(file) {
    const xhr = new XMLHttpRequest();
    const url = '/upload';
    const fd = new FormData();
    fd.append('video', file, file.name);

    xhr.open('POST', url, true);

    xhr.upload.onprogress = function (e) {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
      }
    };

    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        // Replace the page with result HTML from server
        document.open();
        document.write(xhr.responseText);
        document.close();
      } else {
        setStatus('Upload failed. Server returned ' + xhr.status);
        enableUpload(true);
      }
    };

    xhr.onerror = function () {
      setStatus('Upload error. Check your connection.');
      enableUpload(true);
    };

    enableUpload(false);
    setStatus('Uploading...');
    xhr.send(fd);
  }

  // init
  if (dropzone && fileInput) {
    clearSelection();
  }
});
