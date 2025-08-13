import gradio as gr
import datetime
import os
import shutil
from pathlib import Path
import tempfile

# Configuration
OUTPUT_DIR = Path("user_data")
OUTPUT_DIR.mkdir(exist_ok=True)
EXAMPLE_IMG = "esempio_foto.png"  # Assicurati che questo file esista nella stessa directory dello script

# Italian/English options
SKIN_CARE_PRODUCTS = [
    "Idratante / Moisturizer", "Lenitiva / Soothing", "Contro l'acne / Anti-acne", "Antirughe / Anti-wrinkle",
    "Anti-invecchiamento / Anti-aging", "Protezione solare / Sunscreen", "Schiarente / Brightening",
    "Contro le macchie / Anti-spots", "Nessuna crema utilizzata / No cream used"
]

USAGE_FREQUENCY = [
    "Mai / Never", "Raramente / Rarely", "1-2 volte a settimana / 1-2 times a week",
    "3-4 volte a settimana / 3-4 times a week", "Ogni giorno / Every day", "Più volte al giorno / Multiple times a day"
]

SKIN_TYPES = [
    "Pelle secca / Dry skin",
    "Pelle grassa / Oily skin",
    "Pelle mista / Combination skin",
    "Pelle normale / Normal skin",
    "Pelle sensibile / Sensitive skin",
    "Pelle disidratata / Dehydrated skin"
]

SKIN_CONDITIONS = [
    "Presenza costante di rossore / Constant redness",
    "Macchie cutanee / Skin spots",
    "Presenza di acne / Acne presence",
    "Lentiggini / Freckles",
    "Pelle atopica / Atopic skin",
    "Couperose / Couperose",
    "Rosacea / Rosacea",
    "Dermatite / Dermatitis",
    "Pelle spenta/opaca / Dull skin",
    "Pori dilatati / Enlarged pores",
    "Rughe marcate / Pronounced wrinkles",
    "Pelle sottile / Thin skin",
    "Nessuna condizione particolare / No particular condition"
]

# Create birth year list from 1940 to 2010
BIRTH_YEARS = [str(year) for year in range(1940, 2011)]

def save_user_data(year, gender, exposure, area, products, frequency, 
                  skin_type, skin_conditions, skin_description, photo_file, video_file, consent):
    """Save user data and handle both image and video properly"""
    if not consent:
        return "❌ **Devi accettare il trattamento dei dati / You must accept data processing** per procedere con la registrazione."
    
    # Entrambi foto E video sono obbligatori
    if not photo_file:
        return "❌ **È obbligatorio fornire una foto del viso per procedere con la registrazione. / It is mandatory to provide a photo of your face to proceed with registration.**"
    
    if not video_file:
        return "❌ **È obbligatorio fornire un video del viso per procedere con la registrazione. / It is mandatory to provide a video of your face to proceed with registration.**"
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save text data
        user_file = OUTPUT_DIR / f"user_{timestamp}.txt"
        with open(user_file, "w", encoding="utf-8") as f:
            f.write(f"""
            DATA REGISTRAZIONE / REGISTRATION DATE: {datetime.datetime.now()}
            
            INFORMAZIONI PERSONALI / PERSONAL INFORMATION:
            - Anno di nascita / Year of birth: {year}
            - Sesso / Gender: {gender}
            - Esposizione ambientale / Environmental exposure: {exposure}
            - Zona / Area: {area}
            
            AUTOVALUTAZIONE PELLE / SKIN SELF-ASSESSMENT:
            - Tipo di pelle / Skin type: {skin_type}
            - Condizioni cutanee / Skin conditions: {', '.join(skin_conditions) if skin_conditions else 'Nessuna / None'}
            - Breve descrizione della pelle / Brief skin description: {skin_description if skin_description else 'Nessuna / None'}
            
            CURA DEL VISO / FACE CARE:
            - Prodotti utilizzati / Products used: {', '.join(products) if products else 'Nessuno / None'}
            - Frequenza d'uso / Usage frequency: {frequency}
            """)
        
        # Handle photo file
        if photo_file and Path(photo_file).is_file():
            photo_extension = os.path.splitext(photo_file)[1].lower() if os.path.splitext(photo_file)[1] else ".png" 
            photo_path = OUTPUT_DIR / f"photo_{timestamp}{photo_extension}"
            shutil.copy2(photo_file, photo_path)
            # Pulisci il file temporaneo di Gradio
            if "gradio_temp" in Path(photo_file).name and Path(photo_file).exists():
                os.remove(photo_file)
        else:
            return "❌ Errore nel salvataggio della foto / Error saving photo: file non valido o non trovato / invalid or not found."

        # Handle video file
        if video_file and Path(video_file).is_file():
            video_extension = os.path.splitext(video_file)[1].lower() if os.path.splitext(video_file)[1] else ".mp4"
            video_path = OUTPUT_DIR / f"video_{timestamp}{video_extension}"
            shutil.copy2(video_file, video_path)
            if ("gradio_temp" in Path(video_file).name) and Path(video_file).exists(): # Controlla anche qui per gradio_temp
                os.remove(video_file)
        else:
            return "❌ Errore nel salvataggio del video / Error saving video: file non valido o non trovato / invalid or not found."
        
        return "✅ **Registrazione completata con successo! / Registration completed successfully!** Grazie per il tuo contributo / Thank you for your contribution."
    
    except Exception as e:
        return f"❌ **Errore durante la registrazione / Error during registration**: {str(e)}. Si prega di riprovare o contattare il supporto / Please try again or contact support."


# Improved dark theme with better contrast
dark_theme = gr.themes.Default(
    primary_hue="indigo",
    secondary_hue="slate",
    neutral_hue="stone"
).set(
    button_primary_background_fill="#4b6cb7",
    button_primary_background_fill_hover="#3a56a0",
    button_primary_text_color="#ffffff",
    background_fill_primary="#1a1a2e",
    background_fill_secondary="#16213e",
    block_background_fill="#1a1a2e",
    block_label_background_fill="#16213e",
    block_label_text_color="#ffffff",
    block_title_text_color="#ffffff",
    body_text_color="#e6e6e6",
    border_color_primary="#4b6cb7",
    checkbox_label_text_color="#e6e6e6",
    input_background_fill="#16213e",
    slider_color="#4b6cb7"
)

with gr.Blocks(theme=dark_theme, title="Registrazione Utente - Studio Cosmetologico") as demo:
    # Title and introduction
    gr.Markdown("""
    # Studio Cosmetologico - Raccolta Dati / Cosmetological Study - Data Collection
    
    Questo questionario ha lo scopo di raccogliere informazioni utili per la ricerca cosmetologica 
    sull'invecchiamento cutaneo e problematiche della pelle del viso in relazione a fattori ambientali e stili di vita. 
    I dati raccolti saranno trattati in forma anonima e utilizzati esclusivamente per scopi di ricerca.
    
    This questionnaire aims to collect useful information for cosmetological research 
    on skin aging and facial skin problems in relation to environmental factors and lifestyles. 
    The collected data will be processed anonymously and used exclusively for research purposes.
    """, elem_classes=["header-text"])
    
    # Main form
    with gr.Row():
        with gr.Column():
            gr.Markdown("## 📝 Informazioni Personali / Personal Information", elem_classes=["header-text"])
            
            birth_year = gr.Dropdown(
                label="Anno di Nascita / Year of Birth",
                choices=BIRTH_YEARS,
                value="1980",
                elem_classes=["input-field"]
            )
            
            gender = gr.Radio(
                label="Sesso / Gender",
                choices=["Maschile / Male", "Femminile / Female"],
                value="Maschile / Male",
                elem_classes=["radio-field"]
            )
            
            exposure = gr.Dropdown(
                label="Esposizione Ambientale / Environmental Exposure",
                choices=[
                    "Lavoro all'aperto / Outdoor work",
                    "Esposizione solare frequente / Frequent sun exposure",
                    "Clima estremo / Extreme climate",
                    "Ambiente controllato / Controlled environment"
                ],
                value="Ambiente controllato / Controlled environment",
                elem_classes=["input-field"]
            )
            
            area = gr.Radio(
                label="Zona / Area",
                choices=["Città / City", "Mare / Sea", "Montagna / Mountain", "Campagna / Countryside"],
                value="Città / City",
                elem_classes=["radio-field"]
            )
        
        with gr.Column():
            gr.Markdown("## 💆 Cura del Viso / Face Care", elem_classes=["header-text"])
            
            products = gr.CheckboxGroup(
                label="Prodotti Utilizzati / Products Used",
                choices=SKIN_CARE_PRODUCTS,
                elem_classes=["checkbox-field"]
            )
            
            frequency = gr.Dropdown(
                label="Frequenza d'Uso / Usage Frequency",
                choices=USAGE_FREQUENCY,
                value="Mai / Never",
                elem_classes=["input-field"]
            )
            
            gr.Markdown("## 🔍 Autovalutazione della Pelle / Skin Self-Assessment", elem_classes=["header-text"])
            
            skin_type = gr.Radio(
                label="Come definiresti la tua pelle? / How would you define your skin?",
                choices=SKIN_TYPES,
                value="Pelle normale / Normal skin",
                elem_classes=["radio-field"]
            )
            
            skin_conditions = gr.CheckboxGroup(
                label="Condizioni cutanee presenti (seleziona tutte quelle applicabili) / Existing skin conditions (select all that apply)",
                choices=SKIN_CONDITIONS,
                elem_classes=["checkbox-field"]
            )

            skin_description = gr.Textbox(
                label="Breve descrizione della tua pelle (facoltativo) / Brief description of your skin (optional)",
                placeholder="Es: La mia pelle è sensibile al freddo e tende a seccarsi d'inverno. / E.g.: My skin is sensitive to cold and tends to dry out in winter.",
                lines=3,
                elem_classes=["input-field"]
            )
            
            # Titolo della sezione Foto e Video (Entrambi Obbligatori)
            gr.Markdown("## 📸 Foto e Video del Viso (Entrambi Obbligatori) / Face Photo and Video (Both Mandatory)", elem_classes=["header-text"]) 
            gr.Markdown("""
            Per questo studio, è **obbligatorio fornire SIA una foto CHE un breve video** del tuo viso.
            Segui attentamente le indicazioni per ciascuna acquisizione.
            
            ---
            
            For this study, it is **mandatory to provide BOTH a photo AND a short video** of your face.
            Please follow the guidelines carefully for each acquisition.
            """, elem_classes=["photo-instructions"])

            # Example Image (now always visible)
            gr.Image(
                EXAMPLE_IMG,
                label="Foto di Esempio (per riferimento) / Example Photo (for reference)",
                height=200,
                interactive=False,
                elem_classes=["example-image"]
            )

            # --- SEZIONE FOTO (Obbligatoria) ---
            gr.Markdown("### Opzioni Foto (Obbligatoria) / Photo Options (Mandatory)", elem_classes=["sub-header-text"]) # Sub-Header
            with gr.Tabs() as photo_tabs: 
                with gr.TabItem("Scatta foto / Take Photo"):
                    gr.Markdown("""
                    **Istruzioni per la Foto:**
                    * **Buona illuminazione:** Assicurati che il viso sia ben illuminato e senza ombre.
                    * **Metti a fuoco il viso:** La foto deve essere nitida e focalizzata sul viso.
                    * **Niente che copra il viso:** Non indossare occhiali, cappelli, maschere o altri accessori che possano coprire il viso o la pelle.
                    ---
                    **Photo Instructions:**
                    * **Good lighting:** Make sure your face is well-lit and without shadows.
                    * **Focus on your face:** The photo must be clear and focused on your face.
                    * **Nothing covering your face:** Do not wear glasses, hats, masks, or other accessories that might cover your face or skin.
                    """, elem_classes=["media-instructions"])
                    
                    # Componente per la cattura della foto, interactive=True per mostrare il pulsante di scatto
                    photo_webcam_input = gr.Image(
                        label="Scatta la tua foto dalla webcam / Take your photo from webcam",
                        sources=["webcam"],
                        type="filepath", 
                        interactive=True, 
                        elem_classes=["camera-image"]
                    )
                    gr.Markdown("Nota: La fotocamera potrebbe mostrare un'immagine speculare. / Note: The camera might show a mirrored image.", elem_classes=["camera-note"])
                
                with gr.TabItem("Carica foto / Upload Photo"):
                    gr.Markdown("""
                    **Istruzioni per la Foto:**
                    * **Formato:** JPEG, PNG, o BMP.
                    * **Qualità:** Alta risoluzione, viso nitido.
                    * **Nessun filtro o modifica:** La foto deve essere non editata.
                    * **Simile all'esempio:** La foto deve avere caratteristiche simili a quella mostrata nell'esempio.
                    ---
                    **Photo Instructions:**
                    * **Format:** JPEG, PNG, or BMP.
                    * **Quality:** High resolution, clear face.
                    * **No filters or edits:** The photo must be unedited.
                    * **Similar to example:** The photo must have characteristics similar to the one shown in the example.
                    """, elem_classes=["media-instructions"])
                    
                    photo_upload_input = gr.File(
                        label="Carica la tua foto / Upload your photo",
                        type="filepath",
                        file_types=["image"],
                        elem_classes=["file-upload"]
                    )

            # --- SEZIONE VIDEO (Obbligatoria) ---
            gr.Markdown("### Opzioni Video (Obbligatorio) / Video Options (Mandatory)", elem_classes=["sub-header-text"]) # Sub-Header
            with gr.Tabs() as video_tabs: 
                with gr.TabItem("Registra video / Record Video"):
                    gr.Markdown("""
                    **Istruzioni per il Video (Durata Massima: 10 secondi):**
                    * **Illuminazione:** Assicurati che il viso sia ben illuminato e senza ombre.
                    * **Messa a fuoco:** Il viso deve essere a fuoco per tutta la durata del video.
                    * **Espressione Neutra:** Inizia con un'espressione facciale neutra.
                    * **Movimento:** Muovi lentamente il viso da destra a sinistra e poi dall'alto verso il basso (o viceversa) per mostrare diverse angolazioni.
                    * **Niente che copra il viso:** Non indossare occhiali, cappelli o altri accessori che possano coprire il viso.
                    ---
                    **Video Instructions (Maximum Duration: 10 seconds):**
                    * **Lighting:** Ensure your face is well-lit and free of shadows.
                    * **Focus:** Your face should remain in focus throughout the video.
                    * **Neutral Expression:** Start with a neutral facial expression.
                    * **Movement:** Slowly move your face from right to left, then top to bottom (or vice versa) to show different angles.
                    * **Nothing covering your face:** Do not wear glasses, hats, or other accessories that might cover your face.
                    """, elem_classes=["media-instructions"])
                    
                    video_capture_input = gr.Video(
                        label="Registra il tuo video / Record your video",
                        sources=["webcam"],
                        height=300, 
                        elem_classes=["video-capture"]
                        # **MODIFICA:** Rimosso completamente 'webcam_options'
                    )
                    gr.Markdown("Nota: Il video potrebbe non essere speculare. / Note: The video might not be mirrored.", elem_classes=["camera-note"])

                with gr.TabItem("Carica video / Upload Video"):
                    gr.Markdown("""
                    **Istruzioni per il Video Caricato (Durata Massima: 10 secondi):**
                    * **Formato:** MP4, AVI, MOV o WebM.
                    * **Qualità:** Buona risoluzione e nitidezza.
                    * **Contenuto:** Il video deve seguire le stesse indicazioni di movimento e illuminazione descritte per la registrazione diretta.
                    * **Nessun filtro o modifica:** Il video deve essere non editato.
                    ---
                    **Uploaded Video Instructions (Maximum Duration: 10 seconds):**
                    * **Format:** MP4, AVI, MOV, or WebM.
                    * **Quality:** High resolution, clear face.
                    * **No filters or edits:** The photo must be unedited.
                    * **Similar to example:** The photo must have characteristics similar to the one shown in the example.
                    """, elem_classes=["media-instructions"])
                    
                    video_upload_input = gr.File(
                        label="Carica il tuo video / Upload your video",
                        type="filepath",
                        file_types=["video"],
                        elem_classes=["file-upload"]
                    )
    
    # --- Sezione Consenso e Privacy ---
    gr.Markdown("---", elem_classes=["divider"])
    gr.Markdown("## 🔒 Consenso e Privacy / Consent and Privacy", elem_classes=["header-text"])

    with gr.Accordion("Clicca qui per leggere l'Informativa Completa sulla Privacy / Click here to read the Full Privacy Policy", open=False):
        gr.Markdown(f"""
        ### Informativa sulla Privacy (Art. 13 GDPR) / Privacy Policy (Art. 13 GDPR)
        
        **Titolare del Trattamento / Data Controller:** Clair Clinique S.r.l., Strada Statale 17 Loc. Boschetto di Pile, 67100 L'Aquila AQ, admin@pec.clairclinique.com
        
        **Finalità del Trattamento / Purpose of Processing:** I dati personali e la **foto e il video** che ci fornirai saranno raccolti ed elaborati esclusivamente per le seguenti finalità:
        * Ricerca scientifica sull'invecchiamento cutaneo e problematiche della pelle del viso, fattori ambientali e stili di vita.
        * Analisi statistiche e sviluppo di modelli predittivi in ambito cosmetologico.
        * Pubblicazioni scientifiche (solo dati aggregati e anonimi).
        ---
        Your personal data and **photo and video** will be collected and processed exclusively for the following purposes:
        * Scientific research on skin aging and facial skin problems, environmental factors, and lifestyles.
        * Statistical analysis and development of predictive models in cosmetology.
        * Scientific publications (aggregated and anonymous data only).
        
        **Base Giuridica del Trattamento / Legal Basis for Processing:** Il trattamento dei tuoi dati si basa sul tuo **consenso esplicito** (Art. 6, par. 1, lett. a) e Art. 9, par. 2, lett. a) del GDPR per le categorie particolari di dati, come le immagini/video).
        ---
        The processing of your data is based on your **explicit consent** (Art. 6, par. 1, lit. a) and Art. 9, par. 2, lit. a) of the GDPR for special categories of data, such as images/videos).
        
        **Categorie di Dati Raccolti / Categories of Data Collected:**
        * **Dati anagrafici (non identificativi) / Anagraphic data (non-identifying):** Anno di nascita / Year of birth, Sesso / Gender.
        * **Dati geografici / Geographic data:** Zona (città, mare, montagna, campagna) / Area (city, sea, mountain, countryside).
        * **Dati relativi allo stile di vita / Lifestyle data:** Esposizione ambientale / Environmental exposure.
        * **Dati relativi alla salute (autovalutazione) / Health-related data (self-assessment):** Tipo di pelle / Skin type, Condizioni cutanee / Skin conditions, Breve descrizione della pelle / Brief skin description.
        * **Dati relativi alle abitudini di cura / Care habits data:** Prodotti utilizzati / Products used, Frequenza d'uso / Usage frequency.
        * **Dati biometrici (foto e video)**: Una fotografia E un video del viso. / **Biometric data (photo and video)**: A photograph AND a video of the face.
        
        **Modalità del Trattamento / Processing Methods:** I tuoi dati saranno trattati in formato elettronico e cartaceo, con logiche strettamente correlate alle finalità indicate e in modo da garantirne la sicurezza e la riservatezza, nel rispetto dei principi di cui all'Art. 5 del GDPR. Verranno adottate tutte le misure tecniche e organizzative necessarie a ridurre al minimo il rischio di accesso non autorizzato, diffusione, perdita o distruzione dei dati.
        ---
        Your data will be processed in electronic and paper format, with logic strictly related to the indicated purposes and in a way that ensures their security and confidentiality, in compliance with the principles of Art. 5 of the GDPR. All necessary technical and organizational measures will be adopted to minimize the risk of unauthorized access, dissemination, loss, or destruction of data.
        
        **Anonimizzazione e Pseudonimizzazione / Anonymization and Pseudonymization:** Per la ricerca, i dati saranno, ove possibile e appropriato, **anonimizzati** o **pseudonimizzati** in modo da non consentire la tua identificazione diretta. La tua immagine e video saranno utilizzati solo per le finalità di ricerca specificate e non saranno associati al tuo nome o ad altri dati identificativi nelle pubblicazioni o nelle presentazioni.
        ---
        For research purposes, data will be, where possible and appropriate, **anononymized** or **pseudonymized** so as not to allow your direct identification. Your image and video will only be used for the specified research purposes and will not be associated with your name or other identifying data in publications or presentations.
        
        **Conservazione dei Dati / Data Retention:** I dati saranno conservati per il tempo strettamente necessario al perseguimento delle finalità di ricerca, e comunque non oltre **10 anni** dalla data di raccolta, salvo ulteriori obblighi di legge o esigenze di ricerca che richiedano un periodo più lungo, sempre nel rispetto delle normative vigenti.
        ---
        Data will be stored for the time strictly necessary to pursue research purposes, and in any case not beyond **10 years** from the date of collection, unless further legal obligations or research needs require a longer period, always in compliance with current regulations.
        
        **Destinatari dei Dati / Data Recipients:** I tuoi dati non saranno diffusi. Potranno essere condivisi con il personale autorizzato di Clair Clinique S.r.l. coinvolto nella ricerca e con soggetti terzi (es. università, istituti di ricerca) solo se strettamente necessario per le finalità di ricerca e previo accordi di riservatezza e conformità al GDPR.
        ---
        Your data will be shared only with authorized personnel of the Clair Clinique involved in the research and with third parties (e.g., universities, research institutes) only if strictly necessary for research purposes and after confidentiality agreements and GDPR compliance.
        
        **Diritti dell'Interessato / Data Subject Rights:** In qualità di interessato, hai il diritto di:
        * **Accesso / Access** (Art. 15 GDPR): Ottenere la conferma che sia o meno in corso un trattamento di dati personali che ti riguardano e, in tal caso, ottenerne l'accesso. / Obtain confirmation as to whether or not personal data concerning you are being processed, and, where that is the case, access to the personal data.
        * **Rettifica / Rectification** (Art. 16 GDPR): Ottenere la rettifica dei dati personali inesatti che ti riguardano. / Obtain the rectification of inaccurate personal data concerning you.
        * **Cancellazione / Erasure** (Art. 17 GDPR - "diritto all'oblio" / "right to be forgotten"): Ottenere la cancellazione dei dati personali che ti riguardano, se sussistono i motivi previsti dalla legge. / Obtain the erasure of personal data concerning you without undue delay if the grounds provided by law exist.
        * **Limitazione di trattamento / Restriction of processing** (Art. 18 GDPR): Ottenere la limitazione del trattamento. / Obtain restriction of processing.
        * **Portabilità dei dati / Data portability** (Art. 20 GDPR): Ricevere in un formato strutturato, di uso comune e leggibile da dispositivo automatico i dati personali che ti riguardano. / Receive the personal data concerning you, which you have provided to a controller, in a structured, commonly used and machine-readable format.
        * **Opposizione / Objection** (Art. 21 GDPR): Opporsi in qualsiasi momento al trattamento dei dati personali che ti riguardano. / Object at any time to processing of personal data concerning you.
        * **Revoca del consenso / Withdrawal of consent:** Revocare il consenso in qualsiasi momento, senza pregiudicare la liceità del trattamento basata sul consenso prestato prima della revoca. La revoca del consenso comporta l'interruzione del trattamento dei dati a partire dalla data di ricezione della richiesta. / Withdraw consent at any time, without affecting the lawfulness of processing based on consent before its withdrawal. The withdrawal of consent implies the interruption of data processing from the date of receipt of the request.
        * **Reclamo / Complaint** (Art. 77 GDPR): Proporre reclamo all'Autorità Garante per la Protezione dei Dati Personali (Piazza Venezia, 11 - 00187 Roma - protocollo@pec.gpdp.it). / Lodge a complaint with a supervisory authority (Garante per la Protezione dei Dati Personali, Piazza Venezia, 11 - 00187 Roma - protocollo@pec.gpdp.it).
        
        Per esercitare i tuoi diritti, puoi contattare il Titolare del Trattamento all'indirizzo [Contatto Email/PEC o Responsabile della Protezione dei DPO) se presente].
        ---
        To exercise your rights, you can contact the Data Controller at [Email/PEC Contact or DPO if present].
        
        **Natura del Conferimento / Nature of Provision:** Il conferimento dei dati è facoltativo. Tuttavia, il mancato conferimento del consenso o dei dati richiesti potrebbe impedire la partecipazione allo studio di ricerca.
        ---
        The provision of data is optional. However, failure to provide consent or the requested data may prevent participation in the research study.
        """)
    
    consent = gr.Checkbox(
        label="""**Ho letto e compreso l'Informativa sulla Privacy** e acconsento al trattamento dei miei dati personali e della mia **foto e video** per le finalità di ricerca indicate.
        ---
        **I have read and understood the Privacy Policy** and I consent to the processing of my personal data and my **photo and video** for the indicated research purposes.""",
        value=False,
        elem_classes=["consent-checkbox"]
    )
    
    submit = gr.Button("Registrati / Register", variant="primary", elem_classes=["submit-button"])
    output = gr.Textbox(label="Stato della Registrazione / Registration Status", interactive=False, elem_classes=["status-text"])
    
    # Custom CSS for better readability and new image styling
    css = """
    .header-text { color: #ffffff !important; }
    .input-field .label { color: #e6e6e6 !important; }
    .radio-field .label { color: #e6e6e6 !important; }
    .checkbox-field .label { color: #e6e6e6 !important; }
    .file-upload .label { color: #e6e6e6 !important; }
    .status-text { color: #ffffff !important; font-size: 1.1em; }
    .submit-button { font-weight: bold !important; font-size: 1.2em; padding: 10px 20px; }
    .example-image { border: 2px solid #4b6cb7 !important; border-radius: 8px !important; }
    .consent-checkbox { margin-top: 20px !important; margin-bottom: 20px !important; }
    .consent-checkbox .label { color: #e6e6e6 !important; font-size: 16px !important; }
    .camera-image { max-height: 300px !important; }
    .video-capture { max-height: 300px !important; } /* New CSS for video component */
    .tab-item { padding: 15px !important; }
    .camera-note { color: #aaaaaa !important; font-size: 12px !important; font-style: italic !important; }
    .divider { margin-top: 30px; margin-bottom: 30px; border-top: 1px solid #4b6cb7; }
    .gradio-container { max-width: 900px; margin: auto; } /* Centra il contenuto e limita la larghezza */
    .photo-instructions { color: #e6e6e6; font-size: 0.95em; margin-bottom: 15px; background-color: #16213e; padding: 15px; border-radius: 8px; border: 1px solid #4b6cb7; }
    .photo-instructions ul { list-style-type: disc; margin-left: 20px; padding-left: 0; }
    .photo-instructions li { margin-bottom: 5px; }
    
    /* New CSS for embedded example image */
    .example-image-container { 
        text-align: center; /* Center the image and text */
        margin-top: 20px; 
        border: 2px solid #4b6cb7; /* Add a border similar to the old example image */
        border-radius: 8px; /* Rounded corners */
        padding: 10px; /* Some padding inside the border */
        background-color: #1a1a2e; /* Match block background */
    }
    .embedded-example-image {
        max-width: 100%; /* Ensure image scales within its container */
        height: auto;
        max-height: 200px; /* Limit height as before */
        display: block; /* Remove extra space below image */
        margin: 0 auto; /* Center the image itself within its container */
    }
    .example-image-container p {
        margin-top: 10px; /* Space between image and its description */
        font-size: 0.85em;
        color: #e6e6e6;
    }
    .media-instructions {
        color: #e6e6e6;
        font-size: 0.9em;
        background-color: #213054; /* Slightly different background for instructions within tabs */
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        border: 1px solid #3a56a0;
    }
    .sub-header-text { /* New CSS for the sub-headers */
        color: #ffffff !important;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 1px solid #4b6cb7;
        padding-bottom: 5px;
    }
    """
    demo.css = css
    
    # Form submission
    submit.click(
        save_user_data,
        inputs=[
            birth_year, gender, exposure, area, products, frequency, 
            skin_type, skin_conditions, skin_description, 
            photo_webcam_input, 
            video_capture_input,
            consent
        ],
        outputs=output
    )
    
    # Listener per l'upload della foto: il file caricato va a photo_webcam_input
    photo_upload_input.change(
        lambda x: x,
        inputs=photo_upload_input,
        outputs=photo_webcam_input 
    )

    # Listener per l'upload del video: il file caricato va a video_capture_input
    video_upload_input.change(
        lambda x: x,
        inputs=video_upload_input,
        outputs=video_capture_input
    )


if __name__ == "__main__":
    demo.launch(share=True)
