# AI Reel Factory — Starter v1

This starter creates one vertical 9:16 MP4 from a topic using:
- Gemini API for an original Hindi/Hinglish script
- edge-tts for a Hindi voiceover
- Pillow for a designed vertical background
- FFmpeg for final MP4 + subtitles
- GitHub Actions for cloud execution

## Important
- This is a starter MVP, not a full cinematic AI video generator.
- It creates one designed background with voiceover and timed captions.
- Free API quotas and service availability can change.
- `edge-tts` uses an online Microsoft Edge speech service; it is not an official paid production API and may change or be rate-limited.
- Gemini free-tier content handling and quotas are governed by Google's current terms. Do not send private or sensitive information.
- Instagram and YouTube publishing is NOT automatic in v1. Download the MP4 and upload it yourself.
- Do not publish copyrighted music or footage without rights.

## Setup on iPhone
1. Sign in to GitHub and create a **Public** repository named `ai-reel-factory`.
2. Upload all files/folders from this ZIP to the repository, keeping the folder structure.
3. Open https://aistudio.google.com/ and create a Gemini API key.
4. In GitHub, open your repository:
   Settings → Secrets and variables → Actions → New repository secret
   Name: `GEMINI_API_KEY`
   Secret: paste your API key. Never put the key in `main.py` or a public file.
5. Open the repository's Actions tab.
6. Choose `Create AI Reel` → `Run workflow`.
7. Enter a topic and press `Run workflow`.
8. When the run finishes, open it and download the `ai-reel-mp4` artifact.
9. Unzip it in the Files app. Your video is `reel.mp4`.

## Change the Hindi voice
In `.github/workflows/create-reel.yml`, change:
`TTS_VOICE: hi-IN-SwaraNeural`
Other voice names can be checked in the edge-tts voice list. Voice availability may change.

## Troubleshooting
- `GEMINI_API_KEY` missing/invalid: recreate the secret carefully.
- Quota or 429 error: wait for quota reset or use fewer generations.
- TTS connection error: retry later; the online speech service may be unavailable.
- FFmpeg error: check the workflow log in Actions.

## Free usage note
GitHub Actions standard runners are free for public repositories under GitHub's current policy. Gemini free tier has model-specific rate limits. No service is unlimited or guaranteed free forever.
