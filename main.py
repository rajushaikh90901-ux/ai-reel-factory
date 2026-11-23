import os, re, json, asyncio, subprocess, textwrap, sys
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont
import edge_tts

OUT = Path("output")
OUT.mkdir(exist_ok=True)

def gemini_script(topic):
    api_key = os.environ["GEMINI_API_KEY"]
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = f"""
Create an original 35-45 second Hindi/Hinglish motivational/educational short video script about: {topic}
Return ONLY valid JSON with keys:
title: short title (max 8 words)
narration: natural spoken Hindi/Hinglish, 75-95 words, no markdown
visual_keyword: 2-4 simple English words describing a background mood
Make it engaging, accurate, and avoid unsupported claims.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {"contents":[{"parts":[{"text":prompt}]}],
            "generationConfig":{"temperature":0.8, "responseMimeType":"application/json"}}
    req = Request(url, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"}, method="POST")
    with urlopen(req, timeout=180) as response:
        data = json.loads(response.read().decode())
    raw = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(raw)

def find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]
    for f in candidates:
        if Path(f).exists():
            return f
    return None

def make_background(title):
    character = Image.open("9DA24A7D-BCB3-44BF-8E72-FA669452D455.png").convert("RGB")
    character = character.resize((1080, 1920))
    character.save(OUT / "background.png")

def get_audio_duration(path):
    result = subprocess.check_output([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)
    ], text=True).strip()
    return float(result)

def make_srt(text, duration):
    words = text.split()
    chunks = [" ".join(words[i:i+6]) for i in range(0,len(words),6)]
    total_chars = sum(max(1,len(c)) for c in chunks)
    cursor = 0.0
    lines = []
    for idx, chunk in enumerate(chunks, 1):
        span = duration * max(1,len(chunk)) / total_chars
        start, end = cursor, min(duration, cursor+span)
        def stamp(sec):
            ms = int(sec*1000)
            hh, rem = divmod(ms,3600000); mm, rem = divmod(rem,60000); ss, milli = divmod(rem,1000)
            return f"{hh:02}:{mm:02}:{ss:02},{milli:03}"
        lines += [str(idx), f"{stamp(start)} --> {stamp(end)}", chunk, ""]
        cursor = end
    (OUT/"captions.srt").write_text("\n".join(lines), encoding="utf-8")

async def make_voice(text):
    voice = os.getenv("TTS_VOICE", "hi-IN-SwaraNeural")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(OUT/"voice.mp3"))

def render():
    audio = OUT/"voice.mp3"
    duration = get_audio_duration(audio)
    make_srt(SCRIPT["narration"], duration)
    # Escape path for ffmpeg subtitles filter.
    srt = str((OUT/"captions.srt").resolve()).replace("\\", r"\\").replace(":", r"\:")
    vf = (
        "scale=1080:1920,"
        f"subtitles='{srt}':force_style='FontName=DejaVu Sans,FontSize=18,"
        "Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101020,"
        "BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=210,MarginL=70,MarginR=70'"
    )
    subprocess.run([
        "ffmpeg","-y","-loop","1","-i",str(OUT/"background.png"),"-i",str(audio),
        "-vf",vf,"-t",str(duration),"-r","30","-c:v","libx264","-preset","ultrafast",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest",
        str(OUT/"reel.mp4")
    ], check=True)

if __name__ == "__main__":
    topic = os.getenv("REEL_TOPIC", "Discipline beats motivation")
    SCRIPT = gemini_script(topic)
    (OUT/"script.json").write_text(json.dumps(SCRIPT, ensure_ascii=False, indent=2), encoding="utf-8")
    asyncio.run(make_voice(SCRIPT["narration"]))
    make_background(SCRIPT["title"])
    render()
    print("DONE: output/reel.mp4")
