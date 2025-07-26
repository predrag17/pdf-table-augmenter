# pdf-table-augmenter

Welcome to pdf-table-augmenter, platform where you can augment tables while parsing pdf documents!

## Overview

pdf-table-augmenter is a platform that enhances tables extracted from PDF documents by analyzing the surrounding text—before and after each table—to provide context and generate meaningful descriptions. This helps users understand what each table represents, improving clarity and usability of the extracted data.

---

## Features

1. **Upload pdf file**: Upload pdf file and give information about all the tables in the pdf in separate format for each table.
2. **File-Specific Conversation**: A dedicated conversation for each uploaded file, focused exclusively on discussing and analyzing the extracted and explained tables within that document.

---

## Tech Stack

pdf-table-augmenter is built using modern web technologies to ensure scalability, performance, and flexibility.

### Backend:

- **Django Rest Framework**: Facilitates the creation of RESTful APIs, allowing seamless integration with the frontend.
- 
### Frontend:

- **Next.js with TypeScript**: A modern framework that combines the performance and flexibility of Next.js with the safety and developer experience of TypeScript, enabling scalable, type-safe web applications.

### AI and Processing:

- **LangChain**: Powers context-aware analysis by connecting table content with surrounding text to generate meaningful table descriptions and augmentations.
- **LLM Integration**: Uses large language models to analyze and enhance tables based on document context, improving accuracy and usability.
- **Text Classification & Structuring**: Identifies relevant sections around tables and classifies them to support intelligent augmentation and context generation.

---

## Installation & Setup

### Prerequisites

Ensure you have the following installed on your system:

- Python 3.9+
- Node.js 16+
- 
### Environment Variables

Create a `.env` file in the `backend` and `frontend` directories and add necessary environment variables (e.g., database credentials, API keys).

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-table-augmenter.git
cd pdf-table-augmenter/pdf-table-augmenter-api

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

### Frontend Setup

```bash
cd pdf-table-augmenter/pdf-table-augmenter-frontend

# Install dependencies
npm install

# Start the Next.js development server
npm run dev
```
