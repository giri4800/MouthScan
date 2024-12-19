document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('startCamera');
    const captureButton = document.getElementById('captureImage');
    const video = document.getElementById('camera');
    const canvas = document.getElementById('preview');
    let stream = null;

    if (startButton) {
        startButton.addEventListener('click', async function() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: 'environment',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                });
                
                video.srcObject = stream;
                video.classList.remove('d-none');
                await video.play();
                
                startButton.classList.add('d-none');
                captureButton.classList.remove('d-none');
            } catch (err) {
                console.error('Error accessing camera:', err);
                alert('Failed to access camera. Please ensure camera permissions are granted.');
            }
        });
    }

    if (captureButton) {
        captureButton.addEventListener('click', async function() {
            if (stream) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                const context = canvas.getContext('2d');
                context.drawImage(video, 0, 0);
                
                // Stop camera stream
                stream.getTracks().forEach(track => track.stop());
                video.classList.add('d-none');
                canvas.classList.remove('d-none');
                
                // Convert canvas to blob
                canvas.toBlob(async function(blob) {
                    const formData = new FormData();
                    formData.append('image', blob, 'capture.jpg');
                    
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
                }, 'image/jpeg', 0.8);
            }
        });
    }
});
