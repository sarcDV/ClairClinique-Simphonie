import gradio as gr
import cv2
import mediapipe as mp
import numpy as np

# Inizializza MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_face_detection = mp.solutions.face_detection

# Variabile globale per l'immagine catturata
captured_image = None

# Funzione per disegnare la mesh sul frame
def draw_face_mesh(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
            )
    return frame

# Funzione per disegnare il box della face detection
def draw_face_detection_box(frame):
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(frame_rgb)
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return frame

# Funzione per estrarre e ridimensionare il volto
def crop_and_resize_face(frame):
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(frame_rgb)
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                face_crop = frame[y:y + h, x:x + w]
                face_resized = cv2.resize(face_crop, (224, 224))  # Ridimensiona a 224x224
                return face_resized
    return None

# Funzione per generare un modello 3D del volto
def generate_3d_face_model(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    if results.multi_face_landmarks:
        # Crea un'immagine vuota per il modello 3D
        face_3d = np.zeros((224, 224, 3), dtype=np.uint8)
        for face_landmarks in results.multi_face_landmarks:
            for idx, landmark in enumerate(face_landmarks.landmark):
                x, y = int(landmark.x * 224), int(landmark.y * 224)
                cv2.circle(face_3d, (x, y), 2, (255, 255, 255), -1)  # Disegna i landmarks
        return face_3d
    return None

# Funzione per catturare un frame e aggiornare l'immagine catturata
def capture_frame(video_feed):
    global captured_image
    captured_image = video_feed.copy()  # Salva il frame corrente
    return captured_image  # Restituisci l'immagine catturata

# Funzione principale per lo streaming della webcam
def webcam_view(dummy_input):
    cap = cv2.VideoCapture(1)  # Usa 0 per la webcam principale (usa 1 se hai più webcam)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Converti il frame da BGR (OpenCV) a RGB (Gradio)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        yield frame_rgb

    cap.release()

# Funzione per caricare un'immagine
def load_file(file):
    try:
        # Leggi il file caricato
        file_path = file.name
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Carica un'immagine
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Impossibile leggere l'immagine. Verifica il formato del file.")
            captured_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Converti in RGB
            return captured_image
        else:
            raise ValueError("Formato file non supportato. Carica un'immagine PNG/JPG.")
    except Exception as e:
        print(f"Errore durante il caricamento del file: {str(e)}")
        return None

# Funzione per generare le cinque immagini
def generate_images(input_image):
    original_image = input_image.copy()  # Immagine originale
    image_with_mesh = draw_face_mesh(input_image.copy())  # Immagine con mesh
    face_detection_image = draw_face_detection_box(input_image.copy())  # Immagine con box
    cropped_face_image = crop_and_resize_face(input_image.copy())  # Volto estratto
    face_3d_model = generate_3d_face_model(input_image.copy())  # Modello 3D
    return original_image, image_with_mesh, face_detection_image, cropped_face_image, face_3d_model

# Interfaccia Gradio
with gr.Blocks() as demo:
    gr.Markdown("# Simphonie")
    gr.Markdown("### Your Personal AI Skin Analyzer")

    with gr.Row():
        # Video della webcam
        webcam_output = gr.Image(label="Webcam Feed", elem_id="webcam-feed")
        # Immagine originale senza mesh
        original_image_output = gr.Image(label="Immagine Originale", elem_id="original-image")
        # Immagine con mesh
        mesh_image_output = gr.Image(label="Immagine con Mesh", elem_id="mesh-image")

    with gr.Row():
        # Immagine con il box della face detection
        face_detection_image_output = gr.Image(label="Face Detection", elem_id="face-detection-image")
        # Crop del volto
        cropped_face_image_output = gr.Image(label="Volto Estratto", elem_id="cropped-face-image")
        # Modello 3D del volto
        face_3d_model_output = gr.Image(label="Modello 3D del Volto", elem_id="face-3d-model")

    # Pulsante per catturare un frame
    capture_button = gr.Button("Cattura Screenshot")

    # Pulsante per caricare un file
    file_upload = gr.File(label="Carica Immagine")

    # Pulsante per analizzare un'immagine caricata
    analyze_button = gr.Button("Analizza Immagine")

    # Funzione per gestire il pulsante di cattura
    def handle_capture(video_feed):
        if video_feed is None:
            return None, None, None, None, None  # Nessun frame disponibile
        # Cattura l'immagine originale
        original_image = capture_frame(video_feed)
        # Genera le cinque immagini
        return generate_images(original_image)

    # Funzione per gestire il caricamento di un'immagine
    def handle_file_upload(file):
        input_image = load_file(file)
        if input_image is None:
            return None, None, None, None, None  # File non valido
        # Genera le cinque immagini
        return generate_images(input_image)

    # Collega i pulsanti alle funzioni
    capture_button.click(
        fn=handle_capture,
        inputs=webcam_output,
        outputs=[original_image_output, mesh_image_output, face_detection_image_output, cropped_face_image_output, face_3d_model_output]
    )

    analyze_button.click(
        fn=handle_file_upload,
        inputs=file_upload,
        outputs=[original_image_output, mesh_image_output, face_detection_image_output, cropped_face_image_output, face_3d_model_output]
    )

    # Streaming della webcam
    demo.load(
        webcam_view,
        inputs=None,
        outputs=webcam_output,
        every=0.1  # Aggiorna ogni 100ms
    )

# Avvia l'applicazione
demo.launch()