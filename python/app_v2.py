import gradio as gr
import cv2
import mediapipe as mp
import numpy as np

# Inizializza MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

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

        # Se è stato catturato un frame, restituisci anche l'immagine catturata
        if captured_image is not None:
            # Genera due versioni dell'immagine:
            original_image = captured_image.copy()  # Immagine originale senza mesh
            image_with_mesh = draw_face_mesh(captured_image.copy())  # Immagine con mesh
            yield frame_rgb, original_image, image_with_mesh
        else:
            yield frame_rgb, None, None

    cap.release()

# Interfaccia Gradio
with gr.Blocks() as demo:
    gr.Markdown("# Applicazione Simphonie")
    gr.Markdown("### Analisi del Viso con MediaPipe")

    with gr.Row():
        # Video della webcam (senza mesh)
        webcam_output = gr.Image(label="Webcam Feed", elem_id="webcam-feed")
        # Immagine originale senza mesh
        original_image_output = gr.Image(label="Immagine Originale", elem_id="original-image")
        # Immagine con mesh
        mesh_image_output = gr.Image(label="Immagine con Mesh", elem_id="mesh-image")

    # Pulsante per catturare un frame
    capture_button = gr.Button("Cattura Screenshot")

    # Funzione per gestire il pulsante di cattura
    def handle_capture(video_feed):
        if video_feed is None:
            return None, None  # Nessun frame disponibile
        # Cattura l'immagine originale
        original_image = capture_frame(video_feed)
        # Genera l'immagine con la mesh
        image_with_mesh = draw_face_mesh(original_image.copy())
        return original_image, image_with_mesh

    # Collega il pulsante alla funzione di cattura
    capture_button.click(
        fn=handle_capture,
        inputs=webcam_output,
        outputs=[original_image_output, mesh_image_output]
    )

    # Streaming della webcam
    demo.load(
        webcam_view,
        inputs=None,
        outputs=[webcam_output, original_image_output, mesh_image_output],
        every=0.1  # Aggiorna ogni 100ms
    )

# Avvia l'applicazione
demo.launch()