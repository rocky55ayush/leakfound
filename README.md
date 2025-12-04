🔍 LeakFound – AI-Powered Data Breach Detection System

LeakFound is an AI-based data breach monitoring and risk assessment tool that detects leaked data using machine-learning models trained on SQL logs and database patterns. The system helps security teams quickly identify breaches and assess their severity.

🚀 Features

AI-based SQL Injection Detection using a trained SQL risk model (sql_model.pkl)

Database Leak Identification using database pattern recognition (risk_model.pkl)

Automated Comparison Engine for checking leaked data (compare.csv)

Log Analysis using real-world data (logs.csv)

Risk Scoring System to classify threats into severity levels

Modular Python Structure for easy integration

📁 Project Structure
├── README.md                 # Project documentation  
├── sql AI/                   # SQL detection model files  
│   ├── sql AI  
│   └── sql_model.pkl  
├── database AI model/        # Database risk model files  
│   ├── database AI model  
│   └── risk_model.pkl  
├── logs.csv                  # Training data for SQL analysis  
├── compare.csv               # Sample leaked dataset  
├── test.py                   # Script to run and test predictions  

🧠 How It Works

Log Analyzer reads SQL logs and database entries

Machine Learning Models detect malicious or leaked data

Risk Model assigns severity scores

Prediction Engine (test.py) returns results with accuracy and confidence

▶️ Running the Model
python3 test.py


This executes the AI models and displays risk predictions.

🎯 Objective

To build an automated, lightweight, AI-driven system that can detect leaked data, identify SQL-based threats, and provide a risk score to help organizations respond faster to possible breaches.
