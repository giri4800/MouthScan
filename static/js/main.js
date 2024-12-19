document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();

    // Image preview functionality
    const imageFile = document.getElementById('imageFile');
    const imagePreview = document.getElementById('imagePreview');

    if (imageFile) {
        imageFile.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.classList.remove('d-none');
                    imagePreview.querySelector('img').src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Form submission handling
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('image', imageFile.files[0]);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    window.location.href = `/analysis/${result.analysis_id}`;
                } else {
                    throw new Error('Upload failed');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to upload image. Please try again.');
            }
        });
    }

    // PWA installation prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
    });

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});
