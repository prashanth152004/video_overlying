#!/bin/bash
mkdir -p services
cd services
touch __init__.py
touch video_service.py
touch speech_service.py
touch translation_service.py
touch voice_service.py
touch audio_mixer.py
touch subtitle_service.py
touch qc_service.py
touch utils.py
cd ..
echo "Microservices skeleton created."
