# 🔴 Live Polling / Quiz Application

A real-time **Live Polling / Quiz Application** developed for the **Software Development Club Technical Team Task Round 2026–27**.

The application allows a host to create a poll, generate a unique room code, allow participants to join, start voting, display live results, and end the poll with final results.

---

## 🎯 Project Track

**Track 1 – Full-Stack Web Development**

**Task:** Live Polling / Quiz Application

---

## 🚀 Features

### 👨‍💼 Admin / Host

- Create a poll with a question
- Add 2–6 answer options
- Generate a unique 6-character room code
- View the number of connected participants
- Start the voting session
- Receive live voting updates
- View live results
- End the poll
- Display final results and winner

### 👥 Participants

- Join a poll using a room code
- Enter a waiting room before voting begins
- Receive the poll question in real time
- Select and submit an answer
- Receive immediate vote confirmation
- Prevent duplicate voting
- View live results
- View final results after the poll ends

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| Flask | Web application framework |
| Flask-SocketIO | Real-time server communication |
| HTML | Web page structure |
| CSS | Styling and responsive design |
| JavaScript | Frontend functionality |
| Socket.IO | Real-time communication |

---

## 📂 Project Structure

```text
SDC_POLLING-APP/
│
├── app.py
│
├── README.md
│
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── admin.html
│   ├── participant.html
│   └── results.html
│

└── static/
    ├── style.css
    └── script.js
