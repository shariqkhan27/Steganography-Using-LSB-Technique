# 🔐 Advanced Image Steganography System

## Overview
Military-grade steganography tool that securely hides encrypted messages within images using LSB technique with AES-256-GCM encryption.

## Features

### 🛡️ Security
- AES-256-GCM encryption before embedding
- PBKDF2 key derivation (100,000 iterations)
- Password-protected messages
- Message authentication and integrity verification

### 🎨 Steganography
- LSB (Least Significant Bit) embedding
- Configurable bits per channel
- Lossless PNG output preservation
- Metadata handling support

### 🖥️ Interface
- Modern CustomTkinter GUI
- Command-line interface
- Real-time image preview
- Progress indicators

### 🔬 Analysis Tools
- Image capacity checker
- Steganalysis detection
- Image comparison tools
- Encoding statistics

## Installation

```bash
pip install -r requirements.txt