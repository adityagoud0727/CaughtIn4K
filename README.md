# CaughtIn4K

**A Localized Media Forensics, Metadata Sanitization, and Cryptographic Steganography Suite**

Final-Year College Project
**Academic Year:** 2026–2027
**Project Author:** Aditya Vikas Goud
**Domain:** Cybersecurity, Cryptography, and Digital Media Forensics

## Overview

CaughtIn4K is a Python desktop application designed to help users examine media files for privacy-sensitive metadata, assess potential privacy risks, sanitize supported images, and explore encrypted steganography.

The application is designed to work locally on the user's computer.

## Features

- **User Authentication:** Local login with password hashing.
- **Media Analysis:** Analyze supported images and inspect available metadata.
- **Privacy Risk Assessment:** Display a risk score and detected findings.
- **Metadata Sanitization:** Create a cleaned image without the original image metadata.
- **PixelVault:** Hide and extract encrypted messages in supported images.
- **Reports:** Generate JSON analysis reports.
- **Audit History:** Review recorded application activities.
- **Local Database:** Store user and analysis records using SQLite.

## Technology Stack

- Python
- CustomTkinter
- SQLite
- Pillow
- Argon2 password hashing
- Cryptography for encrypted steganography

## Project Structure

```text
CaughtIn4K/
+-- app/
¦   +-- core/
¦   +-- database/
¦   +-- security/
¦   +-- main.py
+-- assets/
+-- create_user.py
+-- test_auth.py
+-- .gitignore
+-- README.md
```

## Running the Application

1. Install a compatible Python version.
2. Install the project's required Python packages.
3. From the project directory, launch the application with:

   ```powershell
   python -m app.main
   ```

The local database and generated reports are maintained on the user's computer and are excluded from this repository.

## Security and Privacy

- Do not commit passwords, private keys, real user databases, private media, or sensitive reports.
- Keep a backup of important local project data.
- Sanitization and steganography support depend on the formats supported by the application.

## Project Status

A working desktop application with media analysis, sanitization, PixelVault, report generation, and audit history.

---
Academic Year 2026–2027


## Installation and Setup

### Prerequisites
- Windows 10 or Windows 11
- Python installed
- Git installed

### Clone the Repository

```powershell
git clone https://github.com/YOUR_USERNAME/CaughtIn4K.git
cd CaughtIn4K
```

Replace `YOUR_USERNAME` with your GitHub username.

### Create a Virtual Environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the environment's Python directly in the next step.

### Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Initialize and Create a User

Initialize the database and create a local user using the project's helper script:

```powershell
python create_user.py
```

Enter the username and password when prompted.

### Run CaughtIn4K

```powershell
python -m app.main
```

### Local Data and Privacy

The application stores its database and generated reports locally. These files are excluded from version control by `.gitignore`. Keep sensitive media and generated reports private.
