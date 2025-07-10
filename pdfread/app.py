from flask import Flask, render_template, request
import fitz  # PyMuPDF
import threading
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def speak(text):
    from gtts import gTTS
    import uuid
    import pygame
    import time

    if not text.strip():
        print("⚠️ No text to speak")
        return

    filename = f"tts_{uuid.uuid4()}.mp3"
    tts = gTTS(text)
    tts.save(filename)

    print("🔊 Playing MP3 with pygame...")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait until audio finishes
    while pygame.mixer.music.get_busy():
        time.sleep(0.5)

    pygame.mixer.quit()
    os.remove(filename)


@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = ""
    if request.method == 'POST':
        file = request.files['pdf_file']
        if file.filename.endswith('.pdf'):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            with fitz.open(filepath) as doc:
                for page in doc:
                    extracted_text += page.get_text()

            if extracted_text.strip():
                threading.Thread(target=speak, args=(extracted_text,), daemon=True).start()
            else:
                print("⚠️ No text extracted from the PDF.")

    return render_template('index.html', text=extracted_text)

if __name__ == '__main__':
    app.run(debug=True)
