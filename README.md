# ModaMood: Co-Creative Fashion Generator

ModaMood is an AI-powered application that helps users discover new outfit concepts based on a moodboard of images. It analyzes the aesthetic of uploaded images and generates a cohesive unified outfit concept using Generative AI. Users can then iteratively refine the result using text commands.

## Features
- **Moodboard Analysis**: Upload 3-6 images to extract style, color, and mood.
- **Aesthetic Synthesis**: Uses Llama 3 to create a unified textual description of your style.
- **AI Image Generation**: Generates high-quality outfit concepts using SD Turbo.
- **Co-Creative Refinement**: Iteratively tweak the design (e.g., "add a red hat", "make it blue") with natural language.
- **Gender-Aware Generation**: Supports Menswear, Womenswear, and Neutral/Unisex styling.

## Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **AI Models**:
    - Captioning: `Salesforce/blip-image-captioning-base` (Local)
    - Summarization: `meta-llama/Meta-Llama-3-8B-Instruct` (HuggingFace API)
    - Generation: `stabilityai/sd-turbo` (Local, MPS-accelerated on Mac)

## Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone <repo_url>
    cd Modamood
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    - Create a `.env` file in the root directory:
      ```
      HF_API_KEY=hf_xxxxxxxxxxxxxxxxx
      ```
    - Get HuggingFace API key from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
    - Needs "Read" permissions for Llama 3

## Running the Application

**Quick Start:**
```bash
./run.sh
```

**Manual Start:**
```bash
# Terminal 1 - Backend
source .venv/bin/activate
uvicorn backend.main:app --reload

# Terminal 2 - Frontend
source .venv/bin/activate
streamlit run frontend/app.py
```

## Usage
1.  Open `http://localhost:8501`
2.  Select target audience (Menswear/Womenswear/Neutral)
3.  Upload 3-6 fashion images
4.  Click **"Analyze Images"**
5.  Click **"Generate Outfit Concept"**
6.  Use "Refine Look" to make adjustments

## System Requirements
- Python 3.9+
- ~6GB disk space (for AI models)
- Apple Silicon Mac recommended (M1/M2/M3 for MPS acceleration)
- Works on Intel Macs and Linux (slower, uses CPU)

## Troubleshooting
- **First run is slow**: Models (~5GB) download on first use
- **API Quota Errors**: HuggingFace free tier has limits; local captioning and generation work offline
- **Memory issues**: Close other apps; models require ~4GB RAM

## License
MIT License
