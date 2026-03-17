# ============================================================
# Media Downloader (MP3 & MP4)
# ============================================================
# Description:
# A Flask-based web app to download audio (MP3) and video (MP4)
# from multiple platforms using a URL.
#
# ------------------------------------------------------------
# Requirements:
# Python 3.8 or above (recommended: 3.10+)
#
# Install Python libraries:
# pip install flask yt-dlp
#
# Install FFmpeg (MANDATORY for audio/video processing):
# Windows:
#   winget install Gyan.FFmpeg
#
# Verify FFmpeg installation:
#   ffmpeg -version
#
# ------------------------------------------------------------
# How to Run:
# 1. Install dependencies
# 2. download the code ,and save it in any folder
# 3. in folder open cmd and type python download.py and press enter
# 4. Run:
#   it will show this link http://127.0.0.1:5000
#   by pressing control just click on it ,you will visit the tool
#
# ------------------------------------------------------------
# Features:
# - Download audio as MP3
# - Download video as MP4
# - Supports multiple platforms (YouTube, Instagram, TikTok, etc.)
#
# ------------------------------------------------------------


from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import time
import threading
import glob

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML = '''
<!doctype html>
<html>
<head><title>Media Downloader</title>
<style>
    body {font-family: Arial; text-align: center; margin-top: 50px; background: #f4f4f4;}
    input {width: 600px; padding: 12px; font-size: 16px; border-radius: 8px; border: 1px solid #ccc;}
    h1 {color: #333;}
    .btn-group {display: flex; justify-content: center; gap: 20px; margin: 25px 0;}
    .fmt-btn {
        padding: 14px 40px;
        font-size: 18px;
        border: 3px solid #ccc;
        border-radius: 10px;
        background: #fff;
        cursor: pointer;
        transition: all 0.2s;
    }
    .fmt-btn.active { background: #4CAF50; color: white; border-color: #4CAF50; }
    #download-btn {
        padding: 14px 50px;
        font-size: 18px;
        background: #2196F3;
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
    }
    #download-btn:hover { background: #1976D2; }
    #download-btn:disabled { background: #aaa; cursor: not-allowed; }
    #status { font-size: 16px; margin-top: 15px; color: #555; }
</style>
</head>
<body>
    <h1>🎬 Media Downloader</h1>
    <input type="text" id="url-input" placeholder="Paste YouTube, TikTok, Instagram link..." />
    <br><br>

    <div class="btn-group">
        <button class="fmt-btn active" id="btn-mp3" onclick="selectFormat('mp3')">🎵 MP3</button>
        <button class="fmt-btn" id="btn-mp4" onclick="selectFormat('mp4')">🎬 MP4</button>
    </div>

    <button id="download-btn" onclick="startDownload()"> Download</button>
    <p id="status"></p>
    <p><small>Supports YouTube, TikTok, Instagram, Twitter, Facebook and more</small></p>

    <script>
        let selectedFormat = 'mp3';

        function selectFormat(fmt) {
            selectedFormat = fmt;
            document.getElementById('btn-mp3').classList.toggle('active', fmt === 'mp3');
            document.getElementById('btn-mp4').classList.toggle('active', fmt === 'mp4');
        }

        function startDownload() {
            const url = document.getElementById('url-input').value.trim();
            if (!url) { alert('Please paste a URL!'); return; }

            const btn = document.getElementById('download-btn');
            btn.disabled = true;
            btn.innerText = ' Downloading...';
            document.getElementById('status').innerText = 'Please wait, this may take a moment...';

            fetch(`/download?url=${encodeURIComponent(url)}&format=${selectedFormat}`)
                .then(res => {
                    if (!res.ok) return res.text().then(t => { throw new Error(t); });
                    return res.blob();
                })
                .then(blob => {
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = selectedFormat === 'mp3' ? 'audio.mp3' : 'video.mp4';
                    a.click();
                    document.getElementById('status').innerText = 'Download complete!';
                    btn.disabled = false;
                    btn.innerText = 'Download';
                })
                .catch(err => {
                    document.getElementById('status').innerText = 'x ' + err.message;
                    btn.disabled = false;
                    btn.innerText = 'Download';
                });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/download')
def download():
    url = request.args.get('url')
    fmt = request.args.get('format', 'mp3')
    if not url:
        return " Please paste a URL", 400

    try:
        timestamp = int(time.time())
        output_template = f'{DOWNLOAD_FOLDER}/{timestamp}_%(title)s.%(ext)s'

        if fmt == 'mp3':
            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
                'noplaylist': True,
                'keepvideo': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'noplaylist': True,
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_path = ydl.prepare_filename(info)

        base = os.path.splitext(raw_path)[0]

        if fmt == 'mp3':
            final_path = base + '.mp3'
            mimetype = 'audio/mpeg'
            ext = 'mp3'
        else:
            final_path = base + '.mp4'
            mimetype = 'video/mp4'
            ext = 'mp4'

        if not os.path.exists(final_path):
            matches = glob.glob(f'{DOWNLOAD_FOLDER}/{timestamp}_*.{ext}')
            if not matches:
                return f"❌ {ext.upper()} file not found. Make sure FFmpeg is installed: winget install Gyan.FFmpeg", 500
            final_path = matches[0]

        return send_file(
            final_path,
            as_attachment=True,
            download_name=os.path.basename(final_path),
            mimetype=mimetype
        )

    except Exception as e:
        error = str(e).lower()
        if any(word in error for word in ["ffmpeg", "ffprobe"]):
            return " FFmpeg not installed. Run: winget install Gyan.FFmpeg", 400
        if any(word in error for word in ["sign in", "age", "private", "unavailable"]):
            return " Video is private or age-restricted.", 400
        return f" Failed: {str(e)[:300]}", 500


if __name__ == '__main__':
    print(" Starting Media Downloader...")
    print("→ Open: http://127.0.0.1:5000")
    print("→ Choose MP3 or MP4 then click Download")
    app.run(host='0.0.0.0', port=5000, debug=False)