# World Prayer App

## Overview

The World Prayer App is an AI-powered web application that empowers people around the globe to spread positivity and affect change through the power of prayer and gratitude. Users can select countries, receive AI-generated prayer points based on current events, and join a global community in prayer for various regions and situations.

![World Prayer App on Desktop and Mobile](https://github.com/guijoe/world-prayer-app/blob/main/images/app.PNG)

## Features

- 🌎 Interactive 3D globe visualization using WebGL
- 🔍 Country selection with detailed information
- ✝️ AI-generated prayer points based on current events
- 🙏 Guided prayer and gratitude suggestions
- 📱 Responsive design for desktop and mobile devices
- 🌐 Multi-language support with news data in English, German, Spanish, and French

## Tech Stack

- **Backend**: Flask (Python)
- **AI Integration**: Google Generative AI API (Gemini)
- **News Data**: Google News Python API (gnews)
- **Database**: SQLite
- **Frontend**: JavaScript, HTML, CSS
- **Visualization**: globe.gl (ThreeJS/WebGL)

## App Architecture

![World Prayer App on Desktop and Mobile](https://github.com/guijoe/world-prayer-app/blob/main/images/architecture.PNG)

## Deployment Guide

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/guijoe/world-prayer-app.git
cd world-prayer-app
```

2. **Create and activate a virtual environment (recommended)**

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory with the following variables:

```
GOOGLE_API_KEY=your_google_api_key
GNEWS_API_KEY=your_gnews_api_key
```

5. **Initialize the database**

```bash
python news_processor.py
```

6. **Run the application**

```bash
python app.py
```

7. **Access the app**

Open your browser and navigate to `http://localhost:5000`

## Extending the App

### Development Environment Setup

1. **Fork the repository on GitHub**

2. **Clone your fork**

```bash
git clone https://github.com/guijoe/world-prayer-app.git
cd world-prayer-app
```

3. **Set up a development environment**

```bash
# Create and activate virtual environment as shown in the Deployment section
# Install dependencies
pip install -r requirements.txt
```

4. **Create a new branch for your feature**

```bash
git checkout -b feature/your-feature-name
```

### Project Structure

```
world-prayer-app/
├── instance/                # Flask instance folder
├── static/                  # Static files (CSS, JS, images)
├── templates/               # HTML templates
├── app.py                   # Main Flask application
├── news_data.db             # Main SQLite database
├── news_data_de.db          # German news database
├── news_data_es.db          # Spanish news database
├── news_data_fr.db          # French news database
└── news_processor.py        # Script to fetch and process news data
```

### Adding New Features

1. **Update the database schema** (if necessary)
   - Modify the database initialization in `news_processor.py`

2. **Add new routes** (if necessary)
   - Update `app.py` with new Flask routes

3. **Create new templates** (if necessary)
   - Add HTML templates to the `templates` directory

4. **Add static assets** (if necessary)
   - Place CSS, JS, or image files in the `static` directory

5. **Test your changes**
   - Run the app locally and verify your feature works as expected

6. **Commit your changes**

```bash
git add .
git commit -m "Add feature: your feature description"
git push origin feature/your-feature-name
```

7. **Create a pull request**
   - Go to the original repository on GitHub
   - Click "New pull request"
   - Select your fork and branch
   - Submit the pull request with a detailed description

## Contributing

We welcome contributions from developers of all backgrounds and experience levels! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape the World Prayer App
- Special thanks to the open-source community for the amazing tools and libraries that made this project possible
