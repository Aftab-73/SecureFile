# 🔒 SecureFile (GUI Edition)

**SecureFile** is a simple and powerful tool that hides your secret files inside normal PNG images. You just need to set a password, and the tool will encrypt your file and put it inside the image. No one will know the secret file is there!

## ✨ What makes this tool special?

* **Very Secure:** It uses AES-256 encryption. This means without the correct password, nobody can open your hidden file.
* **Keeps Images Normal:** The PNG photo will look exactly like a normal photo even after hiding a large file inside it.
* **Easy to Use:** You don't need to type confusing terminal commands. It has a beautiful, dark-themed User Interface (GUI) with buttons.
* **Fast and Smooth:** It can process high-quality images without hanging or freezing your computer.

## 📥 How to Install

1. Download the code from GitHub:
   git clone [https://github.com/Aftab-73/securefile.git](https://github.com/Aftab-73/securefile.git)
   cd securefile
2. Install the required files:
   pip install .

## 📥 How to Run the App

# Open your terminal or command prompt and just type:
securefile

The app will open automatically on your screen!

To Hide a File: Use the "ENCRYPT & HIDE" tab. Select your file, select a normal PNG image, type a password, and click Start.

To Get Your File Back: Use the "EXTRACT & DECRYPT" tab. Select the modified image, type your password, and save your original file.

## 🧪 Testing
This project includes automated tests to make sure no data is lost during the process. To run the tests, use:
pytest tests/
