// DOM Elements
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const uploadGallery = document.getElementById('uploadGallery');
const favoritesGallery = document.getElementById('favoritesGallery');

// Event Listener for File Upload
fileInput?.addEventListener('change', handleFileUpload);
dropZone?.addEventListener('dragover', (e) => e.preventDefault());
dropZone?.addEventListener('drop', handleDrop);

// Handle File Upload
function handleFileUpload(event) {
    const files = event.target.files;
    processFiles(files);
}

// Handle Drag & Drop
function handleDrop(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    processFiles(files);
}

// Process Files & Add to Gallery
function processFiles(files) {
    Array.from(files).forEach(file => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                addScreenshotToGallery(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    });
}

// Add Screenshot to Gallery
function addScreenshotToGallery(imageSrc) {
    const screenshot = document.createElement('div');
    screenshot.classList.add('screenshot');
    
    screenshot.innerHTML = `
        <img src="${imageSrc}" alt="Uploaded Screenshot">
        <button class="fav-btn">❤️</button>
        <button class="remove-btn">❌</button>
    `;
    
    uploadGallery?.appendChild(screenshot);

    // Add event listeners
    screenshot.querySelector('.fav-btn').addEventListener('click', () => addToFavorites(imageSrc));
    screenshot.querySelector('.remove-btn').addEventListener('click', () => screenshot.remove());
}

// Add to Favorites
function addToFavorites(imageSrc) {
    const favScreenshot = document.createElement('div');
    favScreenshot.classList.add('screenshot');
    
    favScreenshot.innerHTML = `
        <img src="${imageSrc}" alt="Favorite Screenshot">
        <button class="remove-btn">❌</button>
    `;
    
    favoritesGallery?.appendChild(favScreenshot);

    // Remove from favorites
    favScreenshot.querySelector('.remove-btn').addEventListener('click', () => favScreenshot.remove());
}
