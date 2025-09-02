# server.py

import http.server
import socketserver
import os
import json
import ast # Per literal_eval
from datetime import datetime
from urllib.parse import unquote # Per gestire URL encoding nei percorsi dei file

import subprocess # Per eseguire comandi esterni
import re         # Per il parsing dell'output dello script

PORT = 8000
UPLOAD_DIR = "users_data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ... (definizione di last_submitted_user_id) ...

def parse_ai_output(output_text):
    """
    Analizza l'output testuale dello script Python AI e lo trasforma in un dizionario.
    Basato sull'esempio fornito nei messaggi precedenti.
    """
    data = {"summary": "", "skin_status": {}}
    lines = output_text.strip().split('\n')
    
    in_summary = False
    in_parameters = False
    in_score = False

    for line in lines:
        line = line.strip()
        if not line: continue

        if line.startswith("--- Analisi dello Stato della Pelle del Viso ---"):
            in_summary = True
            continue
        elif line.startswith("Sommario:"):
            data["summary"] = line[len("Sommario:"):].strip()
            in_summary = False
        elif line.startswith("--- Dettaglio Parametri ---"):
            in_summary = False
            in_parameters = True
            continue
        elif line.startswith("--- Punteggio Complessivo Salute Pelle:"):
            in_parameters = False
            in_score = True
            match = re.search(r"(\d+\.\d+)/100", line)
            if match:
                data["skin_status"]["get_overall_skin_score"] = float(match.group(1))
            continue
        elif line.startswith("---"):
            in_summary = False
            in_parameters = False
            in_score = False
            continue

        if in_parameters:
            match = re.match(r"([^:]+):\s*([\d.]+)", line)
            if match:
                param_name_raw = match.group(1).strip()
                param_value_str = match.group(2).strip()
                # Mappa i nomi italiani ai nomi delle chiavi
                param_key_map = {
                    "Idratazione": "hydration",
                    "Desquamazione": "desquamation_index",
                    "Integrità Barriera": "barrier_integrity",
                    "Luminosità": "brightness",
                    "Uniformità Pigmentazione": "pigmentation_uniformity",
                    "Rossore": "redness_index",
                    "Macchie Melaniniche": "melanin_spot_count",
                    "Levigatezza": "smoothness",
                    "Visibilità Pori": "pore_visibility",
                    "Linee Sottili": "fine_lines_index",
                    "Lucidità": "oiliness",
                    "Comedoni": "comedone_count",
                    "Imperfezioni": "imperfection_count",
                    "Elasticità": "elasticity_score",
                    "Segni Sensibilità": "sensibility_signs",
                }
                param_key = param_key_map.get(param_name_raw)
                if param_key:
                    # Converti il valore: int per conteggi, float per altri
                    if param_key in ["melanin_spot_count", "comedone_count", "imperfection_count"]:
                        data["skin_status"][param_key] = int(param_value_str)
                    else:
                        data["skin_status"][param_key] = float(param_value_str)
    return data

# ... (classe MyHandler) ...

# ... (funzione parse_ai_output) ...

def create_ai_analysis_html(json_data, html_path, user_id):
    """
    Crea la pagina HTML ai_analysis.html usando i dati JSON.
    """
    try:
        is_error = "error" in json_data
        if is_error:
            content = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analisi AI - Errore</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; text-align: center; color: #dc3545; background-color: #f8d7da; }}
        .container {{ max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>❌ Errore nell'Analisi AI</h1>
        <p>{json_data['error']}</p>
        <p>Controlla i log del server per ulteriori dettagli.</p>
    </div>
</body>
</html>"""
        else:
            # --- AGGIUNGI QUESTA LINEA ---
            user_id_js = json.dumps(user_id)  # Per sicurezza, evita injection
            # Template HTML per i risultati validi
            html_template = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analisi AI - Risultati</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f4f7f9; }}
        .container {{ max-width: 800px; margin: auto; background-color: #ffffff; padding: 20px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border-radius: 12px; }}
        h1 {{ color: #333; text-align: center; }}
        .summary {{ background-color: #e9f7ef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .parameters {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; }}
        .parameter-card {{ background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; border-radius: 5px; text-align: center; }}
        .parameter-name {{ font-size: 14px; margin-bottom: 5px; }}
        .parameter-value {{ font-size: 18px; font-weight: bold; color: #007bff; }}
        .overall-score {{ text-align: center; font-size: 24px; font-weight: bold; color: #28a745; margin: 20px 0; }}
        .feedback-section {{ margin-top: 30px; padding: 15px; border-top: 1px solid #eee; }}
        textarea {{ width: 100%; height: 100px; }}
        button {{ padding: 10px 15px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Risultati Analisi AI</h1>
        <div class="summary">
            <h2>📋 Riepilogo</h2>
            <p>{summary}</p>
        </div>
        <h2>📈 Parametri Dettagliati</h2>
        <div class="parameters">
            {parameters_html}
        </div>
        <div class="overall-score">
            ⭐ Punteggio Complessivo: {overall_score}/100
        </div>
        <div class="feedback-section">
            <h2>💭 Il tuo Feedback</h2>
            <p>Come valuti questa analisi?</p>
            <textarea id="feedbackText" placeholder="Scrivi qui il tuo feedback..."></textarea><br><br>
            <button onclick="submitFeedback()">Invia Feedback</button>
            <p id="feedbackMessage" style="display:none; color: green;">Feedback inviato con successo!</p>
        </div>
    </div>
        <script>
        // ✅ userId viene inserito direttamente dal server
        const userId = {user_id_js};

        function submitFeedback() {{
            const feedback = document.getElementById('feedbackText').value;
            if (!feedback) {{
                alert('Per favore, scrivi un feedback prima di inviare.');
                return;
            }}

            if (!userId) {{
                alert("Errore: Impossibile identificare l\'utente.");
                console.error("UserID non disponibile.");
                return;
            }}

            const feedbackPayload = {{
                userId: userId,
                feedback: feedback
            }};

            const button = document.querySelector('button[onclick="submitFeedback()"]');
            const originalButtonText = button ? button.textContent : 'Invia Feedback';
            if (button) {{
                button.disabled = true;
                button.textContent = 'Invio in corso...';
            }}

            fetch('/submit_feedback', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(feedbackPayload)
            }})
            .then(response => {{
                if (!response.ok) {{
                    return response.text().then(text => {{ throw new Error(text); }});
                }}
                return response.json();
            }})
            .then(data => {{
                console.log('Feedback inviato con successo:', data);
                document.getElementById('feedbackMessage').style.display = 'block';
                document.getElementById('feedbackText').value = '';
                setTimeout(() => {{
                    document.getElementById('feedbackMessage').style.display = 'none';
                }}, 3000);
            }})
            .catch((error) => {{
                console.error("Errore durante l\'invio del feedback:", error);
                alert("Errore nell\'invio del feedback: " + error.message);
            }})
            .finally(() => {{
                if (button) {{
                    button.disabled = false;
                    button.textContent = originalButtonText;
                }}
            }});
        }}
    </script>
</body>
</html>
"""
            # Popola il template con i dati
            summary = json_data.get("summary", "Nessun riepilogo disponibile.")
            
            skin_status = json_data.get("skin_status", {})
            overall_score = skin_status.get("get_overall_skin_score", "N/D")
            
            parameters_html = ""
            param_names = {
                "hydration": "Idratazione",
                "desquamation_index": "Desquamazione",
                "barrier_integrity": "Integrità Barriera",
                "brightness": "Luminosità",
                "pigmentation_uniformity": "Uniformità Pigmentazione",
                "redness_index": "Rossore",
                "melanin_spot_count": "Macchie Melaniniche",
                "smoothness": "Levigatezza",
                "pore_visibility": "Visibilità Pori",
                "fine_lines_index": "Linee Sottili",
                "oiliness": "Lucidità",
                "comedone_count": "Comedoni",
                "imperfection_count": "Imperfezioni",
                "elasticity_score": "Elasticità",
                "sensibility_signs": "Segni Sensibilità",
            }
            for key, display_name in param_names.items():
                value = skin_status.get(key)
                if value is not None:
                    # Formatta il valore
                    if isinstance(value, float):
                        # Per parametri 0.0-1.0, mostra come percentuale
                        display_value = f"{value * 100:.0f}%" if key not in ["melanin_spot_count", "comedone_count", "imperfection_count"] else f"{value:.2f}"
                    else:
                        display_value = str(value)
                    parameters_html += f"""
<div class="parameter-card">
    <div class="parameter-name">{display_name}</div>
    <div class="parameter-value">{display_value}</div>
</div>
"""

            # Scrivi il file HTML finale
            content = html_template.format(
                user_id_js=user_id_js,
                summary=summary,
                parameters_html=parameters_html,
                overall_score=f"{overall_score:.2f}" if isinstance(overall_score, (int, float)) else overall_score
            )
            
        with open(html_path, 'w') as f:
            f.write(content)
        print(f"[Server] Pagina HTML dei risultati salvata in {html_path}.")
    except Exception as e:
        print(f"[Server] Errore nella creazione dell'HTML dei risultati: {e}")
        # Crea una pagina HTML di errore di fallback
        with open(html_path, 'w') as f:
            f.write(f"<html><body><h1>Errore</h1><p>Si è verificato un errore nella generazione della pagina dei risultati: {e}</p></body></html>")

# ... (classe MyHandler) ...

# Variabile globale per tenere traccia dell'ultimo utente che ha inviato i dati
# Questo è essenziale per associare la richiesta di analisi AI all'utente corretto.
last_submitted_user_id = None

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Gestisce le richieste GET."""
        # Serve file statici (index.html, js, css, texts, assets)
        # Usa la logica predefinita ma gestisci users_data separatamente se necessario
        if self.path.startswith('/users_data/'):
            self.serve_user_file()
        else:
            super().do_GET()

    def serve_user_file(self):
        """Serve un file dalla directory users_data."""
        # Rimuovi '/users_data/' dall'inizio del path
        relative_path = self.path[len('/users_data/'):]
        # Decodifica eventuali caratteri URL-encoded
        relative_path = unquote(relative_path)
        file_path = os.path.join(UPLOAD_DIR, relative_path)

        # Sicurezza: assicurati che il file richiesto sia all'interno di UPLOAD_DIR
        if not os.path.abspath(file_path).startswith(os.path.abspath(UPLOAD_DIR)):
            self.send_error(403, "Accesso negato.")
            return
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.send_error(404, "File not found.")
            return
        # Limita l'accesso a tipi di file specifici o escludi file sensibili
        forbidden_extensions = ('.py', '.pyc', '.log')
        if file_path.lower().endswith(forbidden_extensions):
             self.send_error(403, "Accesso negato a questo tipo di file.")
             return

        # Usa il metodo della classe base per servire il file
        # Modifica temporaneamente self.path
        original_path = self.path
        try:
            # Costruisci il path relativo corretto
            rel_path = os.path.relpath(file_path, os.getcwd())
            self.path = '/' + rel_path.replace('\\', '/') # Gestisce Windows
            super().do_GET()
        finally:
            self.path = original_path # Ripristina

    def do_POST(self):
        """Gestisce le richieste POST."""
        global last_submitted_user_id # <-- Importante: dichiara la variabile come globale

        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']

            try:
                # --- Parser Multipart Originale (DAI TUOI HTML FUNZIONANTI) ---
                boundary = content_type.split('boundary=')[1].encode()
                data = self.rfile.read(content_length)

                parts = data.split(b'--' + boundary)[1:-1]
                form_data = {}

                for part in parts:
                    headers, content = part.split(b'\r\n\r\n', 1)
                    headers = headers.decode('utf-8')
                    content = content[:-2]

                    if 'filename=' in headers:
                        field_name = headers.split('name="')[1].split('"')[0]
                        form_data[field_name] = content # Bytes
                    else:
                        field_name = headers.split('name="')[1].split('"')[0]
                        form_data[field_name] = content.decode('utf-8') # String
                # --- Fine Parser Multipart Originale ---

                # --- Validazione ed Estrazione Dati ---
                user_id = form_data.get('userId')
                if not user_id:
                    raise Exception("Missing userId")

                # --- Cruciale: Aggiorna la variabile globale ---
                # Memorizza l'ID dell'ultimo utente che ha inviato i dati.
                last_submitted_user_id = user_id
                print(f"[Server] last_submitted_user_id aggiornato a: {last_submitted_user_id}")
                # ------------------------------------------------

                user_dir = os.path.join(UPLOAD_DIR, user_id)
                os.makedirs(user_dir, exist_ok=True)

                # --- Costruzione e Salvataggio di form.json ---
                form_json = {
                    'birthYear': form_data.get('birthYear'),
                    'gender': form_data.get('gender'),
                    'environmentExposure': form_data.get('environmentExposure'),
                    'area': form_data.get('area'),
                    'products': None,
                    'usageFrequency': form_data.get('usageFrequency'),
                    'skinType': None,
                    'skinConditions': None,
                    'skinDescription': form_data.get('skinDescription'),
                    'privacyConsent': form_data.get('privacyConsent'),
                    'timestamp': datetime.now().isoformat()
                }

                def parse_list_field(val):
                    if val is None:
                        return []
                    try:
                        return json.loads(val)
                    except Exception:
                        try:
                            return ast.literal_eval(val)
                        except Exception:
                            if isinstance(val, str):
                                return [v.strip() for v in val.split(',') if v.strip()]
                            return [val]

                form_json['products'] = parse_list_field(form_data.get('products'))
                form_json['skinType'] = parse_list_field(form_data.get('skinType'))
                form_json['skinConditions'] = parse_list_field(form_data.get('skinConditions'))

                with open(os.path.join(user_dir, 'form.json'), 'w', encoding='utf-8') as f:
                    json.dump(form_json, f, ensure_ascii=False, indent=2)

                # --- Salvataggio dei File ---
                if 'selfie' in form_data:
                    with open(os.path.join(user_dir, 'selfie.png'), 'wb') as f:
                        f.write(form_data['selfie'])
                if 'video' in form_data:
                    with open(os.path.join(user_dir, 'video.webm'), 'wb') as f:
                        f.write(form_data['video'])

                # --- Risposta al Client ---
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'folder': user_id}).encode())
                print(f"[Server] Dati salvati con successo per l'utente: {user_id}")

            except Exception as e:
                print(f"[Server] Errore durante l'elaborazione del form: {e}")
                self.send_error(400, f"Error processing request: {str(e)}")

        # --- Gestione per l'avvio dell'AI ---
        elif self.path == '/start_ai_analysis':
            print("[Server] Ricevuta richiesta POST su /start_ai_analysis")
            # Accedi alla variabile globale aggiornata da /submit
            print(f"[Server] UserID recuperato per l'analisi: {last_submitted_user_id}")

            if not last_submitted_user_id:
                print("[Server] Errore: Nessun userID trovato per l'analisi.")
                self.send_error(400, "Nessun utente specificato per l'analisi. Invia prima i dati.")
                return

            user_id = last_submitted_user_id
            user_data_dir = os.path.join(UPLOAD_DIR, user_id)
            selfie_path = os.path.join(user_data_dir, 'selfie.png')
            json_result_path = os.path.join(user_data_dir, 'ai_analysis_result.json')
            html_result_path = os.path.join(user_data_dir, 'ai_analysis.html')

            print(f"[Server] Percorso selfie da analizzare: {selfie_path}")
            print(f"[Server] Percorso risultato JSON: {json_result_path}")
            print(f"[Server] Percorso risultato HTML: {html_result_path}")

            if not os.path.exists(selfie_path):
                print(f"[Server] Errore: File selfie.png non trovato in {selfie_path}")
                self.send_error(404, f"Immagine selfie non trovata per l'utente {user_id}.")
                return

            # 1. Rispondi immediatamente al client che l'analisi è stata avviata
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            html_relative_url = f"/users_data/{user_id}/ai_analysis.html"
            response_data = {
                "message": "Analisi AI avviata con successo.",
                "status": "pending",
                "status_url": html_relative_url
            }
            self.wfile.write(json.dumps(response_data).encode())
            print(f"[Server] Risposta 200 OK inviata al client con status_url: {html_relative_url}")

            # 2. Esegui l'analisi AI in background (VERO, non simulazione)
            print("[Server] Avvio dell'analisi AI in background...")
            try:
                # a. Chiama lo script Python
                # Assicurati che 'python3' sia il comando corretto e che 'skin_test_new.py'
                # sia nella directory corretta o fornisci il percorso completo.
                result = subprocess.run(
                    ['python', 'skin_test_new.py', selfie_path], # <-- Modifica 'skin_test_new.py' se necessario
                    capture_output=True,
                    text=True,
                    check=True, # Solleva CalledProcessError se il comando esce con codice != 0
                    cwd=os.path.dirname(os.path.abspath(__file__)) # Esegue nella directory dello script server.py
                )
                raw_output = result.stdout
                print(f"[Server] Analisi AI completata per utente {user_id}.")

                # b. Analizza l'output e crea il file JSON
                parsed_data = parse_ai_output(raw_output)
                
                with open(json_result_path, 'w') as f:
                    json.dump(parsed_data, f, indent=4)
                print(f"[Server] Risultati JSON salvati in {json_result_path}.")

                # c. Crea la pagina HTML
                create_ai_analysis_html(parsed_data, html_result_path, user_id)
                print(f"[Server] Pagina HTML salvata in {html_result_path}.")

            except subprocess.CalledProcessError as e:
                error_msg = f"Errore nell'esecuzione dello script AI per {user_id}: {e.stderr}"
                print(f"[Server] {error_msg}")
                # Salva anche l'errore in un file
                with open(json_result_path, 'w') as f:
                     json.dump({"error": error_msg}, f)
                # Crea anche una pagina HTML di errore
                create_ai_analysis_html({"error": error_msg}, html_result_path, user_id)
            except Exception as e:
                error_msg = f"Errore interno del server durante l'analisi AI per {user_id}: {str(e)}"
                print(f"[Server] {error_msg}")
                with open(json_result_path, 'w') as f:
                     json.dump({"error": error_msg}, f)
                create_ai_analysis_html({"error": error_msg}, html_result_path, user_id)
        
                # --- Gestione per il salvataggio del Feedback AI ---
        elif self.path == '/submit_feedback':
            print("[Server] Ricevuta richiesta POST su /submit_feedback")
            try:
                # 1. Leggi Content-Length
                content_length_str = self.headers.get('Content-Length')
                print(f"[Server] Content-Length header: '{content_length_str}'")
                if not content_length_str:
                     raise ValueError("Header Content-Length mancante.")
                try:
                    content_length = int(content_length_str)
                except ValueError:
                     raise ValueError(f"Header Content-Length non valido: '{content_length_str}'")

                # 2. Leggi i dati dal body
                print(f"[Server] Tentativo di leggere {content_length} bytes dal body...")
                post_data = self.rfile.read(content_length)
                print(f"[Server] Dati letti (raw bytes): {post_data}")
                print(f"[Server] Dati letti (stringa UTF-8): {post_data.decode('utf-8')}")

                # 3. Parsa i dati come JSON
                try:
                    feedback_data = json.loads(post_data.decode('utf-8'))
                    print(f"[Server] JSON parsato con successo: {feedback_data}")
                except json.JSONDecodeError as je:
                     print(f"[Server] Errore nel parsing JSON: {je}")
                     raise ValueError(f"JSON non valido nel body: {je}")

                # 4. Estrai userId e feedback
                user_id = feedback_data.get('userId')
                feedback_text = feedback_data.get('feedback')
                print(f"[Server] userId estratto: '{user_id}'")
                print(f"[Server] feedback estratto: '{feedback_text}'")

                if not user_id:
                    raise ValueError("Campo 'userId' mancante nel JSON.")
                if not feedback_text:
                     raise ValueError("Campo 'feedback' mancante nel JSON.")

                # --- Da qui in poi il codice originale dovrebbe funzionare ---
                # 5. Costruisci il percorso del file di feedback
                user_data_dir = os.path.join(UPLOAD_DIR, user_id)
                # Verifica che la directory dell'utente esista per sicurezza
                if not os.path.exists(user_data_dir) or not os.path.isdir(user_data_dir):
                     raise ValueError(f"Directory utente non trovata: {user_data_dir}")
                feedback_file_path = os.path.join(user_data_dir, 'ai_analysis_feedback.txt')

                # 6. Salva il feedback in un file di testo
                with open(feedback_file_path, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"[{timestamp}] Feedback dall'utente:\n{feedback_text}\n")
                    f.write("-" * 40 + "\n") # Separatore

                print(f"[Server] Feedback salvato in {feedback_file_path}")

                # 7. Invia una risposta di successo
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"message": "Feedback ricevuto e salvato con successo."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print("[Server] Risposta 200 OK inviata al client.")

            # Gestione specifica degli errori
            except ValueError as ve: # Cattura errori di validazione
                print(f"[Server] Errore di validazione: {ve}")
                self.send_error(400, f"Dati non validi: {ve}")
            except Exception as e: # Cattura qualsiasi altro errore imprevisto
                print(f"[Server] Errore interno imprevisto: {e}")
                self.send_error(500, f"Errore interno del server: {e}")
        # --- Fine gestione Feedback AI ---
        # --- Fine gestione AI ---
        else:
            self.send_error(404)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Uploads will be saved to: {os.path.abspath(UPLOAD_DIR)}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
