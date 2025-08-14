import http.server
import socketserver
import os
import json
from datetime import datetime

PORT = 8000
UPLOAD_DIR = "users_data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']
            
            try:
                # Parse multipart form data
                form_data = self.parse_multipart(content_type, content_length)
                
                # Create user directory
                submission_id = form_data['submission_id']
                user_dir = os.path.join(UPLOAD_DIR, submission_id)
                os.makedirs(user_dir, exist_ok=True)
                
                # Save form data (legacy endpoint, only a few fields)
                with open(os.path.join(user_dir, 'form.json'), 'w') as f:
                    json.dump({
                        'birthYear': form_data.get('birthYear'),
                        'gender': form_data.get('gender'),
                        'area': form_data.get('area'),
                        'timestamp': datetime.now().isoformat()
                    }, f)
                
                # Save selfie
                with open(os.path.join(user_dir, 'selfie.png'), 'wb') as f:
                    f.write(form_data['selfie_image'])
                
                # Save video
                with open(os.path.join(user_dir, 'video.webm'), 'wb') as f:
                    f.write(form_data['video_recording'])
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'folder': submission_id
                }).encode())
                
            except Exception as e:
                self.send_error(400, f"Error processing request: {str(e)}")
        elif self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']
            try:
                form_data = self.parse_multipart(content_type, content_length)
                user_id = form_data.get('userId')
                if not user_id:
                    raise Exception("Missing userId")
                user_dir = os.path.join(UPLOAD_DIR, user_id)
                os.makedirs(user_dir, exist_ok=True)

                # Build form.json with all possible fields from the HTML form
                form_json = {
                    'birthYear': form_data.get('birthYear'),
                    'gender': form_data.get('gender'),
                    'environmentExposure': form_data.get('environmentExposure'),
                    'area': form_data.get('area'),
                    'products': None,
                    'usageFrequency': form_data.get('usageFrequency'),
                    'skinType': form_data.get('skinType'),
                    'skinConditions': None,
                    'skinDescription': form_data.get('skinDescription'),
                    'privacyConsent': form_data.get('privacyConsent'),
                    'timestamp': datetime.now().isoformat()
                }

                # Parse products and skinConditions as lists if possible
                import ast
                def parse_list_field(val):
                    if val is None:
                        return []
                    try:
                        # Try to parse as JSON array
                        return json.loads(val)
                    except Exception:
                        try:
                            # Try to parse as Python list string
                            return ast.literal_eval(val)
                        except Exception:
                            # Fallback: comma separated
                            if isinstance(val, str):
                                return [v.strip() for v in val.split(',') if v.strip()]
                            return [val]
                form_json['products'] = parse_list_field(form_data.get('products'))
                form_json['skinConditions'] = parse_list_field(form_data.get('skinConditions'))

                with open(os.path.join(user_dir, 'form.json'), 'w', encoding='utf-8') as f:
                    json.dump(form_json, f, ensure_ascii=False, indent=2)

                # Save selfie
                if 'selfie' in form_data:
                    with open(os.path.join(user_dir, 'selfie.png'), 'wb') as f:
                        f.write(form_data['selfie'])
                # Save video
                if 'video' in form_data:
                    with open(os.path.join(user_dir, 'video.webm'), 'wb') as f:
                        f.write(form_data['video'])

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'folder': user_id}).encode())
            except Exception as e:
                self.send_error(400, f"Error processing request: {str(e)}")
        else:
            self.send_error(404)

    def parse_multipart(self, content_type, content_length):
        # This is a simplified multipart parser - in production you should use a proper library
        boundary = content_type.split('boundary=')[1].encode()
        data = self.rfile.read(content_length)
        
        parts = data.split(b'--' + boundary)[1:-1]  # First and last parts are boundaries
        form_data = {}
        
        for part in parts:
            headers, content = part.split(b'\r\n\r\n', 1)
            headers = headers.decode('utf-8')
            content = content[:-2]  # Remove trailing \r\n
            
            # Parse headers to get field name and filename
            if 'filename=' in headers:
                # This is a file
                field_name = headers.split('name="')[1].split('"')[0]
                filename = headers.split('filename="')[1].split('"')[0]
                form_data[field_name] = content
            else:
                # This is a regular field
                field_name = headers.split('name="')[1].split('"')[0]
                form_data[field_name] = content.decode('utf-8')
        
        return form_data

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Uploads will be saved to: {os.path.abspath(UPLOAD_DIR)}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")