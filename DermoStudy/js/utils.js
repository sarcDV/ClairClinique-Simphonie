// js/utils.js

// Genera un ID casuale
function generateRandomId(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

// Ottiene un timestamp formattato
function getTimestamp() {
    const d = new Date();
    return d.getFullYear() +
        String(d.getMonth() + 1).padStart(2, '0') +
        String(d.getDate()).padStart(2, '0') +
        String(d.getHours()).padStart(2, '0') +
        String(d.getMinutes()).padStart(2, '0') +
        String(d.getSeconds()).padStart(2, '0');
}

// Converte dataURL in Blob
function dataURLtoBlob(dataurl) {
    if (!dataurl) return null;
    const arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    for (let i = 0; i < n; i++) {
        u8arr[i] = bstr.charCodeAt(i);
    }
    return new Blob([u8arr], { type: mime });
}

// Mostra messaggio di errore
function showError(msg) {
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    errorMessage.textContent = msg;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';

    if (isMobile) {
        setTimeout(() => {
            errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }
}

// Mostra messaggio di successo
function showSuccess(msg) {
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    successMessage.textContent = msg;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';

    if (isMobile) {
        setTimeout(() => {
            successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }
}

// Controlla lo stato del modulo (abilita/disabilita bottone invio)
function checkFormStatus() {
    const selfieTaken = window.selfieTaken || false;
    const videoRecorded = window.videoRecorded || false;
    const privacyConsent = document.getElementById('privacyConsent');
    const submitFormButton = document.getElementById('submitFormButton');

    if (selfieTaken && videoRecorded && privacyConsent.checked) {
        submitFormButton.disabled = false;
        submitFormButton.classList.add('active');
    } else {
        submitFormButton.disabled = true;
        submitFormButton.classList.remove('active');
    }
}

// Espone le funzioni globalmente
window.generateRandomId = generateRandomId;
window.getTimestamp = getTimestamp;
window.dataURLtoBlob = dataURLtoBlob;
window.showError = showError;
window.showSuccess = showSuccess;
window.checkFormStatus = checkFormStatus;