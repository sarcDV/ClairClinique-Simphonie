// js/main.js

document.addEventListener('DOMContentLoaded', async () => {
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    // Carica il contenuto della privacy policy
    try {
        const privacyResponse = await fetch('texts/privacy_it.html');
        const privacyText = await privacyResponse.text();
        document.getElementById('privacyPolicyContent').innerHTML = privacyText;
    } catch (err) {
        console.error('Errore nel caricamento della privacy policy:', err);
        document.getElementById('privacyPolicyContent').textContent = 'Errore nel caricamento del testo.';
    }

    // --- Caricamento Istruzioni Selfie (Foto) ---
    try {
        const selfieInstructionsResponse = await fetch('texts/instructions_photo_it_en.html');
        const selfieInstructionsText = await selfieInstructionsResponse.text();
        
        const selfieContainer = document.getElementById('selfieInstructions');
        if (selfieContainer) {
            selfieContainer.innerHTML = selfieInstructionsText;
        }
    } catch (err) {
        console.error('Errore nel caricamento delle istruzioni selfie:', err);
        const container = document.getElementById('selfieInstructions');
        if (container) {
            container.textContent = 'Errore nel caricamento delle istruzioni per la foto.';
        }
    }

    // --- Caricamento Istruzioni Video ---
    try {
        const videoInstructionsResponse = await fetch('texts/instructions_video_it_en.html');
        const videoInstructionsText = await videoInstructionsResponse.text();
        
        const videoContainer = document.getElementById('videoInstructions');
        if (videoContainer) {
            videoContainer.innerHTML = videoInstructionsText;
        }
    } catch (err) {
        console.error('Errore nel caricamento delle istruzioni video:', err);
        const container = document.getElementById('videoInstructions');
        if (container) {
            container.textContent = 'Errore nel caricamento delle istruzioni per il video.';
        }
    }

    // Abilita il bottone della fotocamera inizialmente
    const startCameraButton = document.getElementById('startCameraButton');
    if (startCameraButton) {
        startCameraButton.disabled = false;
    }

    // Aggiungi stili specifici per mobile se necessario
    if (isMobile) {
        const mediaControls = document.querySelectorAll('.media-controls');
        mediaControls.forEach(control => {
             control.style.position = 'sticky';
             control.style.bottom = '0';
             control.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
             control.style.padding = '10px';
             control.style.zIndex = '100';
        });
    }
});
