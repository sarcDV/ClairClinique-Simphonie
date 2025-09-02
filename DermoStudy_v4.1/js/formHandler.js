// js/formHandler.js

// Elements assumed to be available globally or re-fetched if needed
// For modularity, it's often better to fetch them inside DOMContentLoaded
// or pass them as arguments, but this mimics the original inline script structure.
let submitFormButton, privacyConsent, form;
let selfieTaken = false;
let videoRecorded = false;
let photoData = null;
let videoData = null;
let isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

// Helper: Convert dataURL to Blob (copied from original script)
function dataURLtoBlob(dataurl) {
    if (!dataurl) return null;
    const arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    for (let i = 0; i < n; i++) {
        u8arr[i] = bstr.charCodeAt(i);
    }
    return new Blob([u8arr], { type: mime });
}

// Helper: Generate random ID (copied from original script)
function generateRandomId(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// Helper: Get timestamp (copied from original script)
function getTimestamp() {
    const d = new Date();
    return d.getFullYear() +
        String(d.getMonth() + 1).padStart(2, '0') +
        String(d.getDate()).padStart(2, '0') +
        String(d.getHours()).padStart(2, '0') +
        String(d.getMinutes()).padStart(2, '0') +
        String(d.getSeconds()).padStart(2, '0');
}

// Function to check form status (copied and slightly adapted)
function checkFormStatus() {
    // Ensure elements are available
    if (!submitFormButton) {
         submitFormButton = document.getElementById('submitFormButton');
    }
    if (!privacyConsent) {
        privacyConsent = document.getElementById('privacyConsent');
    }
    if (!form) {
        form = document.getElementById('verificationForm');
    }
    // Enable submit if selfie, video, and privacy consent are present
    if (window.selfieTaken && window.videoRecorded && privacyConsent.checked) {
        submitFormButton.disabled = false;
        submitFormButton.classList.add('active');
    } else {
        submitFormButton.disabled = true;
        submitFormButton.classList.remove('active');
    }
}

// Function to show error (copied and slightly adapted)
function showError(msg) {
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');

    if (errorMessage) {
        errorMessage.textContent = msg;
        errorMessage.style.display = 'block';
    }
    if (successMessage) {
        successMessage.style.display = 'none';
    }

    // Scroll to error message on mobile
    if (isMobile) {
        setTimeout(() => {
            if (errorMessage) {
                errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 300);
    }
}

// --- Updated showSuccess function ---
// This version adds the "Avvia Analisi AI" button
function showSuccess(msg) {
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');

    if (successMessage) {
        successMessage.textContent = msg;
        successMessage.style.display = 'block';
    }
    if (errorMessage) {
        errorMessage.style.display = 'none';
    }

    // --- Inizio Aggiunta Bottone Analisi AI ---
    // Rimuovi eventuali bottoni precedenti per sicurezza
    const existingButton = document.getElementById('startAiAnalysisButton');
    if (existingButton) {
        existingButton.remove();
    }

    const startAiButton = document.createElement('button');
    startAiButton.id = 'startAiAnalysisButton';
    startAiButton.type = 'button';
    startAiButton.textContent = '🧠 Avvia Analisi AI / Start AI Analysis';
    startAiButton.style.marginTop = '15px';
    startAiButton.style.padding = '12px 20px';
    startAiButton.style.fontSize = '16px';
    startAiButton.style.backgroundColor = '#28a745'; // Verde
    startAiButton.style.color = '#fff';
    startAiButton.style.border = 'none';
    startAiButton.style.borderRadius = '5px';
    startAiButton.style.cursor = 'pointer';

    // ... (dentro la funzione showSuccess, nella creazione di startAiButton) ...

    startAiButton.addEventListener('click', async () => {
        console.log("[formHandler] Avvio analisi AI richiesto...");
        
        // 1. Disabilita immediatamente il bottone e cambia il testo
        startAiButton.disabled = true;
        const originalText = startAiButton.textContent;
        startAiButton.textContent = '🧠 Avvio in corso... / Starting...';

        try {
            // 2. Chiama il nuovo endpoint del server
            const response = await fetch('/start_ai_analysis', {
                method: 'POST',
            });

            if (response.ok) {
                const data = await response.json();
                console.log("[formHandler] Analisi AI avviata:", data);

                // 3. Invece di aprire una nuova finestra, mostra un messaggio
                // e fornisce un link cliccabile per i risultati futuri.
                const successMessageElement = document.getElementById('successMessage');
                if (successMessageElement) {
                    // Aggiungi un messaggio e un link
                    const analysisLink = document.createElement('a');
                    analysisLink.href = data.status_url; // L'URL fornito dal server
                    analysisLink.textContent = ' Visualizza i risultati dell\'analisi AI';
                    analysisLink.target = '_blank'; // Facoltativo: apre in un nuovo tab al click
                    analysisLink.style.display = 'block';
                    analysisLink.style.marginTop = '10px';
                    analysisLink.style.fontWeight = 'normal';
                    analysisLink.style.color = '#007bff'; // Colore del link
                    analysisLink.style.textDecoration = 'underline';
                    
                    const analysisMessage = document.createElement('div');
                    analysisMessage.textContent = '🧠 Analisi AI avviata. I risultati saranno disponibili a breve.';
                    analysisMessage.style.marginTop = '10px';
                    analysisMessage.appendChild(analysisLink);

                    successMessageElement.appendChild(analysisMessage);
                }
                
                // Il bottone rimane disabilitato dopo un avvio riuscito
                startAiButton.textContent = '🧠 Analisi Avviata / Analysis Started';

            } else if (response.status === 400 || response.status === 404) {
                const errorText = await response.text();
                throw new Error(errorText);
            } else {
                throw new Error(`Errore del server: ${response.status}`);
            }
        } catch (err) {
            console.error("[formHandler] Errore nell'avvio dell'analisi AI:", err);
            alert(`Errore nell'avvio dell'analisi AI: ${err.message}`); // Mostra errore in alert
            // 4. In caso di errore, riabilita il bottone
            startAiButton.disabled = false;
            startAiButton.textContent = originalText; // Ripristina il testo originale
        }
    });


    // Aggiungi il bottone dopo il messaggio di successo
    if (successMessage) {
        successMessage.parentNode.insertBefore(startAiButton, successMessage.nextSibling);
    }
    // --- Fine Aggiunta Bottone Analisi AI ---

    // Scroll to success message on mobile
    if (isMobile) {
        setTimeout(() => {
            if (successMessage) {
                successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 300);
    }
}
// --- Fine Updated showSuccess function ---

// Make functions globally available if needed by other scripts or inline code
window.dataURLtoBlob = dataURLtoBlob;
window.generateRandomId = generateRandomId;
window.getTimestamp = getTimestamp;
window.checkFormStatus = checkFormStatus;
window.showError = showError;
window.showSuccess = showSuccess; // Sovrascrive la versione base con quella che include il bottone
// Espone le variabili di stato
window.selfieTaken = selfieTaken;
window.videoRecorded = videoRecorded;
window.photoData = photoData;
window.videoData = videoData;


document.addEventListener('DOMContentLoaded', () => {
    // Fetch elements on load
    submitFormButton = document.getElementById('submitFormButton');
    privacyConsent = document.getElementById('privacyConsent');
    form = document.getElementById('verificationForm');

    // Populate birth year (copied from original script)
    const birthYearSelect = document.getElementById('birthYear');
    if (birthYearSelect) {
        for (let year = 1940; year <= 2010; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            birthYearSelect.appendChild(option);
        }
        birthYearSelect.value = "1980"; // Set default value
    }

    // Add event listeners
    if (privacyConsent && checkFormStatus) {
        privacyConsent.addEventListener('change', checkFormStatus);
    }

    // Main form submission handler (copied and slightly adapted)
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            // Ensure elements are available
            const errorMessage = document.getElementById('errorMessage');
            const successMessage = document.getElementById('successMessage');
            if (errorMessage) errorMessage.style.display = 'none';
            if (successMessage) successMessage.style.display = 'none';

            // Custom validation for all required fields except the optional textarea
            const requiredSelectors = [
                '#birthYear',
                'input[name="gender"]:checked',
                '#environmentExposure',
                'input[name="area"]:checked',
                'input[name="products"]:checked',
                '#usageFrequency',
                'input[name="skinConditions"]:checked'
            ];

            // Check if at least one skin type is selected
            const skinTypesSelected = form.querySelectorAll('input[name="skinType"]:checked').length > 0;
            if (!skinTypesSelected) {
                showError('Per favore, seleziona almeno un tipo di pelle. / Please select at least one skin type.');
                return;
            }

            let allValid = true;
            for (const selector of requiredSelectors) {
                if (!form.querySelector(selector)) {
                    allValid = false;
                    break;
                }
            }
            if (!allValid) {
                showError('Per favore, compila tutti i campi obbligatori. / Please fill in all required fields.');
                return;
            }
            if (!window.selfieTaken) {
                showError('Devi scattare un selfie. / You need to take a selfie.');
                return;
            }
            if (!window.videoRecorded) {
                showError('Devi registrare un video. / You need to record a video.');
                return;
            }
            if (!privacyConsent.checked) {
                showError('Devi accettare l\'informativa sulla privacy. / You need to accept the privacy policy.');
                return;
            }

            // Gather form data
            const formData = new FormData(form);
            // Get all checked checkboxes for products, skinType, and skinConditions
            formData.set('products', JSON.stringify(Array.from(form.querySelectorAll('input[name="products"]:checked')).map(cb => cb.value)));
            formData.set('skinType', JSON.stringify(Array.from(form.querySelectorAll('input[name="skinType"]:checked')).map(cb => cb.value)));
            formData.set('skinConditions', JSON.stringify(Array.from(form.querySelectorAll('input[name="skinConditions"]:checked')).map(cb => cb.value)));

            // Add selfie and video (using window. variables)
            formData.append('selfie', dataURLtoBlob(window.photoData), 'selfie.png');
            formData.append('video', window.videoData, 'video.webm');

            // Generate user folder name
            const userId = generateRandomId() + '_' + getTimestamp();
            formData.append('userId', userId);

            // Update button state
            if (submitFormButton) {
                submitFormButton.disabled = true;
                submitFormButton.textContent = 'Invio in corso... / Submitting...';
            }

            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    // Use the updated showSuccess function
                    showSuccess('Dati inviati con successo! / Data submitted successfully!');
                    form.reset();
                    const photoCanvas = document.getElementById('photoCanvas');
                    const videoPreview = document.getElementById('videoPreview');
                    if (photoCanvas) photoCanvas.style.display = 'none';
                    if (videoPreview) videoPreview.style.display = 'none';
                    window.selfieTaken = false;
                    window.videoRecorded = false;
                    window.photoData = null;
                    window.videoData = null;
                    checkFormStatus();
                } else {
                    const errText = await response.text();
                    showError('Errore durante l\'invio: ' + errText);
                }
            } catch (err) {
                showError('Errore di rete: ' + err.message);
            } finally {
                if (submitFormButton) {
                    submitFormButton.disabled = false;
                    submitFormButton.textContent = 'Invia Dati / Submit Data';
                }
            }
        });
    }
});