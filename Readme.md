# 🔒 macOS APFS Encryption Manager

## Description
The **macOS APFS Encryption Manager** is a lightweight, local web application built with Python and Panel (HoloViz). It provides a clean, user-friendly Graphical User Interface (GUI) for macOS's native `diskutil` command-line tool. 

Because macOS does not natively support Linux LUKS, this application uses **APFS Encrypted**, Apple's native military-grade (AES-XTS) block-level encryption standard. It allows users to easily secure external drives, ensuring data is completely inaccessible when the drive is detached or locked.

**⚠️ IMPORTANT NOTE:** This application relies on the native macOS `diskutil` binary. It **must** be run natively on a Mac host. It will not work inside a Linux-based Docker container or on Windows.

## Functionalities
* **Format & Provision:** Wipe a physical external drive and format it directly to an APFS Encrypted volume.
* **Lock / Unlock:** Quickly mount (unlock) or unmount (lock) encrypted APFS volumes using your passphrase.
* **Password Management:** Safely change the encryption passphrase, or remove encryption entirely (decrypt back to standard APFS).
* **Safe Drive Parsing:** Automatically filters out your Mac's internal system drive to prevent accidental formatting, displaying only valid external physical drives and synthesized APFS volumes.
* **Audit Logging:** Automatically logs all lock, unlock, format, and password change attempts to a daily CSV file.

---

## Folder Structure
```text
App/
├── README.md                 # Project documentation
├── app.py                    # Main Panel web UI application
├── requirements.txt          # Python dependencies
├── run.sh                    # Mac execution script
├── utils/
│   ├── __init__.py
│   └── encrypt.py            # Core logic mapping to macOS diskutil
└── logs/                     # Auto-generated directory for action logs
    └── logs-yymmdd.csv

## How to User (Local Set-Up)

## Prerequisites
- A Mac running macOS (APFS support required).
- Python 3.8+ installed.

## Execution
Open your macOS Terminal and navigate to the project folder:
> cd path/to/App

Make sure the run script is executable (you only need to do this once):
> chmod +x run.sh

Install the required Python packages:
> pip install -r requirements.txt

Run the application:
> ./run.sh

The application will automatically open in your default web browser at 
> http://localhost:8510.