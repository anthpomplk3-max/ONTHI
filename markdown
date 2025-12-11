# Audio Dataset

## 📁 File Structure
- `audio/raw/`: Original recordings
- `audio/processed/`: Cleaned and normalized
- `audio/samples/`: 30-second previews
- `metadata/`: JSON files with track info

## 🎵 Audio Specifications
- Format: MP3, WAV
- Sample Rate: 44.1kHz
- Bit Depth: 16-bit
- Channels: Stereo

## 📊 Statistics
- Total duration: 5.2 hours
- Number of files: 124
- Total size: 2.1 GB (with LFS)

## 🚀 Quick Start
```bash
# Clone with LFS
git lfs clone https://github.com/username/audio-repo.git

# Play audio (requires VLC)
vlc audio/processed/sample.wav
