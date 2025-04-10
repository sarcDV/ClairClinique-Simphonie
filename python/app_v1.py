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

        # Disegna la mesh sul frame
        frame_with_mesh = draw_face_mesh(frame)

        # Converti il frame da BGR (OpenCV) a RGB (Gradio)
        frame_rgb = cv2.cvtColor(frame_with_mesh, cv2.COLOR_BGR2RGB)

        # Se è stato catturato un frame, restituisci anche l'immagine catturata
        if captured_image is not None:
            yield frame_rgb, captured_image
        else:
            yield frame_rgb, None

    cap.release()

# Interfaccia Gradio
with gr.Blocks() as demo:
    gr.Markdown("# Applicazione Simphonie")
    gr.Markdown("### Analisi del Viso con MediaPipe")

    with gr.Row():
        # Video della webcam
        webcam_output = gr.Image(label="Webcam Feed", elem_id="webcam-feed")
        # Immagine catturata
        captured_output = gr.Image(label="Screenshot", elem_id="captured-image")

    # Pulsante per catturare un frame
    capture_button = gr.Button("Cattura Screenshot")

    # Funzione per gestire il pulsante di cattura
    def handle_capture(video_feed):
        return capture_frame(video_feed)

    # Collega il pulsante alla funzione di cattura
    capture_button.click(
        fn=handle_capture,
        inputs=webcam_output,
        outputs=captured_output
    )

    # Streaming della webcam
    demo.load(
        webcam_view,
        inputs=None,
        outputs=[webcam_output, captured_output],
        every=0.1  # Aggiorna ogni 100ms
    )

# Avvia l'applicazione
demo.launch()

# import gradio as gr
# import cv2

# # Funzione per catturare il frame corrente della webcam
# def webcam_view():
#     cap = cv2.VideoCapture(1)  # Usa 0 per la webcam principale (usa 1 se hai più webcam)
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         # Converti il frame da BGR (OpenCV) a RGB (Gradio)
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         yield frame_rgb  # Genera il frame per lo streaming
#     cap.release()

# # Crea l'interfaccia Gradio
# app = gr.Interface(
#     fn=webcam_view,
#     inputs=None,
#     outputs=gr.Image(label="Webcam Feed"),  # Output è un'immagine
#     live=True  # Abilita lo streaming live
# )

# # Avvia l'applicazione
# app.launch()
