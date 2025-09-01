// js/formHandler.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('verificationForm');
    const privacyConsent = document.getElementById('privacyConsent');
    const submitFormButton = document.getElementById('submitFormButton');
    const birthYearSelect = document.getElementById('birthYear');

    // Popola l'anno di nascita
    for (let year = 1940; year <= 2010; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        birthYearSelect.appendChild(option);
    }
    birthYearSelect.value = "1980";

    privacyConsent.addEventListener('change', window.checkFormStatus);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        document.getElementById('errorMessage').style.display = 'none';
        document.getElementById('successMessage').style.display = 'none';

        const requiredSelectors = [
            '#birthYear',
            'input[name="gender"]:checked',
            '#environmentExposure',
            'input[name="area"]:checked',
            'input[name="products"]:checked',
            '#usageFrequency',
            'input[name="skinConditions"]:checked'
        ];

        const skinTypesSelected = form.querySelectorAll('input[name="skinType"]:checked').length > 0;
        if (!skinTypesSelected) {
            window.showError('Per favore, seleziona almeno un tipo di pelle. / Please select at least one skin type.');
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
            window.showError('Per favore, compila tutti i campi obbligatori. / Please fill in all required fields.');
            return;
        }
        if (!window.selfieTaken) {
            window.showError('Devi scattare un selfie. / You need to take a selfie.');
            return;
        }
        if (!window.videoRecorded) {
            window.showError('Devi registrare un video. / You need to record a video.');
            return;
        }
        if (!privacyConsent.checked) {
            window.showError('Devi accettare l\'informativa sulla privacy. / You need to accept the privacy policy.');
            return;
        }

        const formData = new FormData(form);
        formData.set('products', JSON.stringify(Array.from(form.querySelectorAll('input[name="products"]:checked')).map(cb => cb.value)));
        formData.set('skinType', JSON.stringify(Array.from(form.querySelectorAll('input[name="skinType"]:checked')).map(cb => cb.value)));
        formData.set('skinConditions', JSON.stringify(Array.from(form.querySelectorAll('input[name="skinConditions"]:checked')).map(cb => cb.value)));
        formData.append('selfie', window.dataURLtoBlob(window.photoData), 'selfie.png');
        formData.append('video', window.videoData, 'video.webm');
        const userId = window.generateRandomId() + '_' + window.getTimestamp();
        formData.append('userId', userId);

        submitFormButton.disabled = true;
        submitFormButton.textContent = 'Invio in corso... / Submitting...';
        try {
            const response = await fetch('/submit', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                window.showSuccess('Dati inviati con successo! / Data submitted successfully!');
                form.reset();
                document.getElementById('photoCanvas').style.display = 'none';
                document.getElementById('videoPreview').style.display = 'none';
                window.selfieTaken = false;
                window.videoRecorded = false;
                window.photoData = null;
                window.videoData = null;
                window.checkFormStatus();
            } else {
                const errText = await response.text();
                window.showError('Errore durante l\'invio: ' + errText);
            }
        } catch (err) {
            window.showError('Errore di rete: ' + err.message);
        } finally {
            submitFormButton.disabled = false;
            submitFormButton.textContent = 'Invia Dati / Submit Data';
        }
    });
});