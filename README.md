# Transcription API

A speech-to-text transcription API built with OpenAI's Whisper models, supporting multi-language audio transcription with code-switching capabilities.

## Overview

This project is a **speech-to-text prototype** that uses the **OpenAI API** (`gpt-4o-transcribe` / `whisper-1`) to transcribe multi-language audio while keeping each word in its original language or script. The output is plain text only, designed for high-accuracy transcription with custom lexicon support.

## Key Features

- **Multi-language transcription** with code-switching support
- **Custom lexicon** for domain-specific terms (drug names, brand names, etc.)
- **Supports WAV, MP3, and M4A** audio formats
- **Post-processing layer** to maintain original language/script
- **Feedback & learning system** for continuous improvement
- **Plain text output** optimized for accuracy

## Requirements

- Python 3.10 or higher
- PostgreSQL database
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd transcription-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Project Structure

```
transcription-api/
├── src/                 # Application source code
├── tests/              # Test files (unit, integration)
├── config/             # Configuration files
├── pyproject.toml      # Project metadata and dependencies
├── README.md           # This file
└── .gitignore          # Git ignore patterns
```

## Configuration

Configuration will be managed through environment variables. See the next setup stage for details.

## Development

This project is in early development as a proof of concept (PoC) for client demos.

## License

TBD
