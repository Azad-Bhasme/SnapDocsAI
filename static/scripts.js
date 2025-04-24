// Drag-and-drop functionality
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

if (dropZone && fileInput) {
  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-blue-500');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-blue-500');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-blue-500');
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
    }
  });
}

// Preview uploaded image
const previewImage = (event) => {
  const file = event.target.files[0];
  if (file) {
    const preview = document.getElementById('preview');
    const reader = new FileReader();
    reader.onload = () => {
      preview.src = reader.result;
      preview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  }
};

if (fileInput) {
  fileInput.addEventListener('change', previewImage);
}
