// js/selfieHandler.js

let currentStream = null;
window.selfieTaken = false;
window.photoData = null;

document.addEventListener('DOMContentLoaded', () => {
    const startCameraButton = document.getElementById('startCameraButton');
    const captureButton = document.getElementById('captureButton');
    const retakeButton = document.getElementById('retakeButton');
    const selfieVideoElement = document.getElementById('selfieVideoElement');
    const photoCanvas = document.getElementById('photoCanvas');

    startCameraButton.addEventListener('click', async () => {
        try {
            if (currentStream) currentStream.getTracks().forEach(t => t.stop());
            // Modifica qui per iOS
            currentStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { ideal: "user" } }
            });
            selfieVideoElement.srcObject = currentStream;
            selfieVideoElement.style.display = 'block';
            // Aggiunto per iOS
            selfieVideoElement.playsInline = true;
            await selfieVideoElement.play(); // Await play for iOS
            photoCanvas.style.display = 'none';
            captureButton.disabled = false;
            startCameraButton.disabled = true;
            document.getElementById('errorMessage').style.display = 'none';
            const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
            if (isMobile) {
                setTimeout(() => {
                    const controls = document.querySelector('.selfie-section .media-controls');
                    controls.scrollIntoView({ behavior: 'smooth', block: 'end' });
                }, 500);
            }
        } catch (err) {
            console.error('Camera error:', err);
            window.showError('Errore: permesso fotocamera negato. / Error: camera permission denied.');
        }
    });

    captureButton.addEventListener('click', () => {
        if (!currentStream) return;
        photoCanvas.width = selfieVideoElement.videoWidth;
        photoCanvas.height = selfieVideoElement.videoHeight;
        const canvasContext = photoCanvas.getContext('2d');
        canvasContext.drawImage(selfieVideoElement, 0, 0, photoCanvas.width, photoCanvas.height);
        window.photoData = photoCanvas.toDataURL('image/png');
        selfieVideoElement.style.display = 'none';
        photoCanvas.style.display = 'block';
        captureButton.style.display = 'none';
        retakeButton.style.display = 'inline-block';
        currentStream.getTracks().forEach(t => t.stop());
        currentStream = null;
        window.selfieTaken = true;
        document.getElementById('recordButton').disabled = false;
        window.checkFormStatus();
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        if (isMobile) {
            setTimeout(() => {
                photoCanvas.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        }
    });

    retakeButton.addEventListener('click', () => {
        photoCanvas.style.display = 'none';
        captureButton.style.display = 'inline-block';
        retakeButton.style.display = 'none';
        document.getElementById('startCameraButton').disabled = false;
        window.photoData = null;
        window.selfieTaken = false;
        window.checkFormStatus();
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        if (isMobile) {
            setTimeout(() => {
                const controls = document.querySelector('.selfie-section .media-controls');
                controls.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }, 300);
        }
    });
});