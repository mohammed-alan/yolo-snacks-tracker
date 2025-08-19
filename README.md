# 🍫 YOLO Snacks Tracker  

Real-time chocolate bar detection and calorie tracker built with **YOLOv8**, **React**, and **Socket.IO**.  
Detects chocolates like Reese's, Snickers, KitKat, Aero, and Twix through a live camera feed and displays their calories instantly.  

---

## ✨ Features
- 🎥 **Live Camera Feed**: Real-time object detection using YOLO.  
- 🍫 **Chocolate Detection**: Supports Reese's, Snickers, KitKat, Aero, and Twix.  
- 🔢 **Confidence Scores**: Displays detection confidence (%) per object.  
- 🔥 **Calorie Tracker**: Automatically maps detected chocolates to their calorie count.  
- ⚡ **Modern UI**: Responsive React frontend with Tailwind CSS.  
- 🔗 **Backend-Frontend Sync**: Live updates using Socket.IO.  


---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/mohammed-alan/yolo-snacks-tracker.git
cd yolo-snacks-tracker
```
### 2️⃣ Backend Setup (YOLO + Python)
Make sure you have Python 3.9+ and install dependencies:

```bash
cd yolo/backend
pip install -r requirements.txt
```
Run the backend:
```bash
python backend.py --model best.pt --source http://192.168.2.27:8080/video --resolution 640x480
```
--model → path to your trained YOLO model

--source → camera feed / video URL

--resolution → input resolution for detection

### 3️⃣ Frontend Setup (React + Tailwind)
Make sure you have Node.js 18+ installed.
```bash
cd frontend/frontend
npm install
npm run dev
```
The frontend will start on http://localhost:5173 (Vite default).

## 🖥️ Usage
Start the backend (YOLO detection).

Start the frontend (React UI).

Open the frontend in your browser.

Watch live detections with chocolate type, confidence %, and calorie info.

## 🛠️ Tech Stack
**YOLOv8** (Ultralytics) – Object detection

**OpenCV** – Video stream handling

**Socket.IO** – Realtime communication

**React + Vite + Tailwind** – Modern frontend


## 📜 License
MIT License – free to use, modify, and share.

---



https://github.com/user-attachments/assets/5d4bf0e8-c074-4f50-956e-e12369c27018

