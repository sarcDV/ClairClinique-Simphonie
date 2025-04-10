// modules/app_initializer.js

// Variabili globali per il modello e la fotocamera
let faceDetectionModel;
let videoStream;

// Funzione per inizializzare l'app
export async function initializeApp() {
    showLoadingScreen();
    updateLoadingStatus("Caricamento dei modelli di intelligenza artificiale...", 20);

    try {
        // Caricamento del modello di rilevamento del viso
        faceDetectionModel = await blazeface.load();
        updateLoadingStatus("Modelli AI caricati con successo!", 60);

        // Inizializzazione della fotocamera
        updateLoadingStatus("Inizializzazione della fotocamera...", 80);
        await setupCamera();

        // Caricamento del modello di valutazione della qualità dell'immagine
        updateLoadingStatus("Caricamento del modello di qualità...", 90);
        await loadQualityModel();

        updateLoadingStatus("App pronta!", 100);

        // Nascondi la schermata di caricamento e mostra l'app
        setTimeout(() => {
            hideLoadingScreen();
            document.getElementById('appContainer').classList.remove('hidden');

            // Aggiungi l'event listener per il pulsante "Scatta Foto"
            document.getElementById('captureButton').addEventListener('click', capturePhoto);

            // Aggiungi l'event listener per il pulsante "Analizza"
            document.getElementById('analyzeButton').addEventListener('click', () => {
                const capturedImage = document.getElementById('capturedImage');
                if (!capturedImage.src || capturedImage.classList.contains('hidden')) {
                    alert("Nessuna immagine catturata. Scatta una foto prima di analizzarla.");
                    return;
                }
                analyzeImageQuality(capturedImage);
            });
        }, 1000);

    } catch (error) {
        console.error('Errore durante l\'inizializzazione:', error);
        updateLoadingStatus("Errore durante l'inizializzazione: " + error.message, 100);
        alert("Si è verificato un errore durante il caricamento dell'app. Per favore ricarica la pagina e assicurati di concedere i permessi della fotocamera.");
    }
}

// Variabile globale per il modello di valutazione della qualità dell'immagine
let qualityModel;

// Funzione per caricare il modello di valutazione della qualità dell'immagine
async function loadQualityModel() {
    try {
        console.log("Tentativo di caricare il modello MobileNet locale...");
        
        // Carica il modello locale
        qualityModel = await tf.loadGraphModel('./models/mobilenet-v2-tensorflow2-100-224-classification-v2/model.json');
        
        console.log("Modello MobileNet locale caricato con successo!");
    } catch (error) {
        console.error('Errore durante il caricamento del modello locale:', error.message);
        console.error('Dettagli completi dell\'errore:', error);
        alert("Si è verificato un errore durante il caricamento del modello locale. Controlla la console per ulteriori dettagli.");
    }
}
// Funzione per mostrare la schermata di caricamento
function showLoadingScreen() {
    document.getElementById('loadingScreen').classList.remove('hidden');
}

// Funzione per nascondere la schermata di caricamento
function hideLoadingScreen() {
    document.getElementById('loadingScreen').classList.add('hidden');
}

// Funzione per aggiornare lo stato di caricamento
function updateLoadingStatus(message, percentage) {
    document.getElementById('loadingStatus').textContent = message;
    document.getElementById('loadingProgressBar').style.width = percentage + '%';
}

// Funzione per inizializzare la fotocamera
async function setupCamera() {
    const video = document.getElementById('cameraFeed');

    try {
        // Access the user's camera
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        videoStream = stream;

        // Wait for the video metadata to load
        return new Promise((resolve) => {
            video.onloadedmetadata = () => {
                resolve();
            };
        });
    } catch (error) {
        console.error('Errore durante l\'accesso alla fotocamera:', error);
        alert("Impossibile accedere alla fotocamera. Assicurati di aver concesso i permessi.");
        throw error; // Re-throw the error to handle it in the calling function
    }
}

// Funzione per catturare una foto dal video
function capturePhoto() {
    const video = document.getElementById('cameraFeed');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas dimensions to match the video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current frame of the video onto the canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert the canvas image to a data URL
    const imageDataUrl = canvas.toDataURL('image/png');

    // Display the captured image
    const capturedImage = document.getElementById('capturedImage');
    capturedImage.src = imageDataUrl;
    capturedImage.classList.remove('hidden'); // Show the captured image

    // Enable and show the "Analizza" button
    const analyzeButton = document.getElementById('analyzeButton');
    analyzeButton.classList.remove('hidden'); // Show the button
    analyzeButton.disabled = false; // Enable the button
}

// Funzione per analizzare la qualità dell'immagine
async function analyzeImageQuality(imageElement) {
    try {
        // Converti l'immagine in un tensore
        const imgTensor = tf.browser.fromPixels(imageElement)
            .resizeNearestNeighbor([224, 224]) // Ridimensiona l'immagine per il modello
            .toFloat()
            .div(255.0) // Normalizza i valori dei pixel
            .expandDims(); // Aggiungi una dimensione batch

        // Effettua la previsione con il modello
        const predictions = await qualityModel.predict(imgTensor).data();

        // Estrai lo score di qualità (assumendo che il modello restituisca un singolo valore di qualità)
        const qualityScore = predictions[0];

        // Mostra i risultati nell'elemento #analysisResults
        const analysisResultsDiv = document.getElementById('analysisResults');
        const qualityScoreParagraph = document.getElementById('qualityScore');

        // Aggiorna il testo con il punteggio di qualità
        qualityScoreParagraph.textContent = `Qualità dell'immagine: ${Math.round(qualityScore * 100)}%`;

        // Mostra il div dei risultati
        analysisResultsDiv.classList.remove('hidden');

        // Verifica se la qualità è sufficiente
        if (qualityScore >= 0.7) { // Soglia di qualità
            alert("La qualità dell'immagine è sufficiente. Procediamo con l'analisi avanzata.");
            // Qui puoi integrare ulteriori funzionalità
        } else {
            alert("La qualità dell'immagine non è sufficiente. Riprova con un'altra foto.");
        }

        // Libera la memoria
        imgTensor.dispose();
    } catch (error) {
        console.error('Errore durante l\'analisi della qualità dell\'immagine:', error);
        alert("Si è verificato un errore durante l'analisi della qualità dell'immagine.");
    }
}