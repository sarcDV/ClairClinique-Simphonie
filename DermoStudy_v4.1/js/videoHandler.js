// js/videoHandler.js (Versione con Debug Esplicito)

(function() { // IIFE per evitare conflitti di scope globali
    'use strict';

    console.log("[videoHandler] Script caricato e IIFE eseguita.");

    // --- 1. Dichiarazione Variabili ---
    let currentStream = null;
    let mediaRecorder = null;
    let recordedChunks = [];
    window.videoRecorded = false;
    window.videoData = null;

    // --- 2. Selezione Elementi DOM ---
    // Questi vengono cercati solo quando il DOM è pronto
    let videoElement, videoPreview, recordButton, stopButton, reRecordButton;

    // --- 3. Inizializzazione al caricamento del DOM ---
    function initVideoHandler() {
        console.log("[videoHandler] Inizializzazione...");
        
        // Seleziona gli elementi
        videoElement = document.getElementById('videoElement');
        videoPreview = document.getElementById('videoPreview');
        recordButton = document.getElementById('recordButton');
        stopButton = document.getElementById('stopButton');
        reRecordButton = document.getElementById('reRecordButton');

        // Controllo esistenza elementi
        if (!videoElement || !videoPreview || !recordButton || !stopButton || !reRecordButton) {
            console.error("[videoHandler] ERRORE CRITICO: Impossibile trovare uno o più elementi DOM necessari.");
            console.error("[videoHandler] videoElement:", videoElement);
            console.error("[videoHandler] videoPreview:", videoPreview);
            console.error("[videoHandler] recordButton:", recordButton);
            console.error("[videoHandler] stopButton:", stopButton);
            console.error("[videoHandler] reRecordButton:", reRecordButton);
            // Mostra un errore visibile all'utente?
            if (recordButton) {
                 recordButton.disabled = true;
                 recordButton.textContent = "Errore Video";
            }
            return; // Esce se gli elementi non sono presenti
        }
        console.log("[videoHandler] Tutti gli elementi DOM trovati con successo.");

        // Inizialmente disabilita i bottoni di controllo
        stopButton.disabled = true;
        reRecordButton.style.display = 'none';
        // recordButton.disabled sarà abilitato da formHandler.js dopo lo scatto della foto

        // --- 4. Aggancio Eventi ---
        console.log("[videoHandler] Aggancio eventi...");
        recordButton.addEventListener('click', handleRecordButtonClick);
        stopButton.addEventListener('click', handleStopButtonClick);
        reRecordButton.addEventListener('click', handleReRecordButtonClick);
        
        console.log("[videoHandler] Inizializzazione completata con successo.");
    }

    // --- 4. Gestori di Evento ---
    async function handleRecordButtonClick() {
        console.log("--- [videoHandler] Bottone 'Avvia Registrazione' cliccato ---");
        if (!videoElement || !recordButton) {
            console.error("[videoHandler] handleRecordButtonClick: Elementi DOM mancanti.");
            return;
        }

        try {
            // Reset e pulizia
            if (currentStream) {
                console.log("[videoHandler] Fermando stream precedente...");
                currentStream.getTracks().forEach(track => track.stop());
                currentStream = null;
            }

            resetVideoUIState();
            recordedChunks = [];
            mediaRecorder = null;
            window.videoData = null;
            window.videoRecorded = false;
            window.checkFormStatus();

            // Richiesta stream (con fallback)
            console.log("[videoHandler] Richiesta stream multimediale...");
            currentStream = await requestMediaStream();
            if (!currentStream) {
                 throw new Error("Impossibile ottenere il flusso multimediale.");
            }

            // Setup video element
            console.log("[videoHandler] Setup elemento video...");
            videoElement.srcObject = currentStream;
            videoElement.style.display = 'block';
            videoElement.playsInline = true;
            await videoElement.play();
            console.log("[videoHandler] Video in riproduzione.");

            // Setup UI registrazione
            videoPreview.style.display = 'none';
            recordButton.disabled = true;
            stopButton.disabled = false;
            reRecordButton.style.display = 'none';

            // Setup MediaRecorder (SENZA mimeType forzato)
            console.log("[videoHandler] Inizializzazione MediaRecorder...");
            mediaRecorder = new MediaRecorder(currentStream);

            // Setup eventi MediaRecorder
            setupMediaRecorderEvents();

            // Avvia registrazione
            console.log("[videoHandler] Avvio registrazione...");
            mediaRecorder.start();
            console.log(`[videoHandler] Stato MediaRecorder dopo start: ${mediaRecorder.state}`);

            // Auto-stop dopo 10s
            console.log("[videoHandler] Impostazione auto-stop...");
            setTimeout(() => {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    console.log("[videoHandler] Auto-stop dopo 10 secondi.");
                    stopRecording();
                } else {
                    console.log(`[videoHandler] Auto-stop: MediaRecorder non in registrazione (stato: ${mediaRecorder?.state || 'null'}).`);
                    finalizeUIAfterStop();
                }
            }, 10000);

        } catch (err) {
            console.error('[videoHandler] ERRORE FATALE durante l\'avvio della registrazione:', err);
            let errorMsg = 'Errore sconosciuto durante l\'avvio della registrazione.';
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMsg = 'Permesso videocamera/microfono negato.';
            } else if (err.name === 'NotFoundError' || err.name === 'OverconstrainedError') {
                errorMsg = 'Dispositivo video/microfono non trovato.';
            } else if (err.name === 'NotReadableError') {
                errorMsg = 'Impossibile accedere alla fotocamera/microfono.';
            } else {
                errorMsg = `Errore: ${err.message || err.name}`;
            }
            console.error("[videoHandler] Messaggio errore mostrato all'utente:", errorMsg);
            window.showError(errorMsg);
            recordButton.disabled = false;
            stopButton.disabled = true;
            reRecordButton.style.display = 'none';
        }
    }

    function handleStopButtonClick() {
        console.log("[videoHandler] Bottone 'Ferma' cliccato.");
        stopRecording();
    }

    function handleReRecordButtonClick() {
        console.log("[videoHandler] Bottone 'Riregistra' cliccato.");
        resetVideoUIState();
        reRecordButton.style.display = 'none';
        recordButton.disabled = false; // Questo dovrebbe essere gestito da formHandler.js
        window.videoData = null;
        window.videoRecorded = false;
        window.checkFormStatus();
    }

    // --- 5. Funzioni di Supporto ---

    async function requestMediaStream() {
        const constraintsWithAudio = { video: { facingMode: { ideal: "user" } }, audio: true };
        const constraintsWithoutAudio = { video: { facingMode: { ideal: "user" } } };

        console.log("[videoHandler] Tentativo 1: video + audio...", constraintsWithAudio);
        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraintsWithAudio);
            console.log("[videoHandler] Stream con audio ottenuto.");
            return stream;
        } catch (audioErr) {
            console.warn("[videoHandler] Tentativo 1 fallito (audio):", audioErr.name);
            if (['NotFoundError', 'NotReadableError', 'OverconstrainedError'].includes(audioErr.name)) {
                console.log("[videoHandler] Tentativo 2: solo video (fallback)...");
                try {
                    const stream = await navigator.mediaDevices.getUserMedia(constraintsWithoutAudio);
                    console.log("[videoHandler] Stream solo video ottenuto.");
                    window.showError("Registrazione video avviata senza audio.");
                    setTimeout(() => {
                         const errorMsgElement = document.getElementById('errorMessage');
                         if (errorMsgElement && errorMsgElement.textContent.includes("audio")) {
                             errorMsgElement.style.display = 'none';
                         }
                    }, 3000);
                    return stream;
                } catch (videoErr) {
                    console.error("[videoHandler] Tentativo 2 fallito (solo video):", videoErr.name);
                    throw videoErr;
                }
            } else {
                throw audioErr;
            }
        }
    }

    function setupMediaRecorderEvents() {
        if (!mediaRecorder) return;

        mediaRecorder.ondataavailable = (event) => {
            console.log(`[videoHandler] MediaRecorder.ondataavailable, chunk size: ${event.data?.size || 0}`);
            if (event.data && event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            console.log("[videoHandler] MediaRecorder.onstop");
            console.log(`[videoHandler] Chunks registrati: ${recordedChunks.length}`);
            if (recordedChunks.length === 0) {
                const errorMsg = 'La registrazione non ha catturato dati.';
                console.warn(`[videoHandler] ${errorMsg}`);
                window.showError(errorMsg);
                finalizeUIAfterStop();
                return;
            }
            try {
                const actualMimeType = mediaRecorder.mimeType || 'video/webm';
                console.log(`[videoHandler] Creazione Blob con mimeType: ${actualMimeType}`);
                const blob = new Blob(recordedChunks, { type: actualMimeType });
                console.log(`[videoHandler] Blob creato, size: ${blob.size} bytes`);
                if (blob.size === 0) {
                    const errorMsg = 'La registrazione ha prodotto un file vuoto.';
                    console.warn(`[videoHandler] ${errorMsg}`);
                    window.showError(errorMsg);
                    finalizeUIAfterStop();
                    return;
                }
                window.videoData = blob;
                videoPreview.src = URL.createObjectURL(blob);
                videoPreview.style.display = 'block';
                videoElement.style.display = 'none';
                if (currentStream) {
                    currentStream.getTracks().forEach(track => track.stop());
                    currentStream = null;
                }
                window.videoRecorded = true;
                window.checkFormStatus();
                console.log("--- [videoHandler] Registrazione completata ---");
            } catch (blobErr) {
                console.error("[videoHandler] Errore creazione Blob:", blobErr);
                window.showError('Errore durante la finalizzazione del video.');
                finalizeUIAfterStop();
            }
        };

        mediaRecorder.onerror = (event) => {
            console.error("[videoHandler] MediaRecorder.onerror", event.error);
            window.showError('Errore registrazione video: ' + (event.error?.message || 'Errore sconosciuto'));
            finalizeUIAfterStop();
            if (mediaRecorder && mediaRecorder.state === "recording") {
                 try { mediaRecorder.stop(); } catch (e) { console.error("[videoHandler] Errore stop dopo errore:", e); }
            }
        };

        mediaRecorder.onstart = () => {
             console.log(`[videoHandler] MediaRecorder.onstart. Stato: ${mediaRecorder.state}`);
        };
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            console.log("[videoHandler] Chiamata mediaRecorder.stop().");
            mediaRecorder.stop();
        } else {
            console.log(`[videoHandler] stopRecording: MediaRecorder non in registrazione (stato: ${mediaRecorder?.state || 'null'}).`);
            finalizeUIAfterStop();
        }
    }

    function resetVideoUIState() {
        if (videoElement) videoElement.style.display = 'none';
        if (videoPreview) videoPreview.style.display = 'none';
        // recordButton.disabled = true; // Non lo resettiamo qui
        if (stopButton) stopButton.disabled = true;
        if (reRecordButton) reRecordButton.style.display = 'none';
    }

    function finalizeUIAfterStop() {
        if (stopButton) stopButton.disabled = true;
        if (reRecordButton) reRecordButton.style.display = 'inline-block';
    }

    // --- 6. Avvio al caricamento del DOM ---
    if (document.readyState === 'loading') {
        console.log("[videoHandler] DOM non ancora caricato, attendo DOMContentLoaded.");
        document.addEventListener('DOMContentLoaded', initVideoHandler);
    } else {
        console.log("[videoHandler] DOM già caricato, esecuzione immediata.");
        // DOM già pronto
        setTimeout(initVideoHandler, 0); // Per garantire l'ordine
    }

})(); // Fine IIFE

console.log("[videoHandler] File videoHandler.js completamente analizzato dal browser.");
