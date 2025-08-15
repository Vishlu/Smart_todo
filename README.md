# 📝 SmartAI ToDo WebApplication

The Smart Todo List is an AI-powered task management web app that helps users efficiently organize daily tasks through intelligent automation. 
It processes context entries from sources like WhatsApp, emails, and notes to generate smart task suggestions, set deadlines, assign priority scores, and categorize tasks automatically.

---

## 🚀 Features
- **Context Processing:** Analyze recent daily context to generate relevant task details.
- **AI Task Suggestions:** Auto-generate task title, description, category, deadline, and priority score using Google Gemini API.
- **CRUD Operations:** Create, read, update, and delete tasks.
- **Context Management:** Add and delete daily context entries to keep data clean.
- **Responsive UI:** HTML, CSS, and JavaScript frontend integrated with DRF backend.
- **Category Suggestions:** AI automatically classifies tasks into categories like Work, Meetings, Email, or Personal.

---

## 🛠 Tech Stack

### **Backend**
- Django
- Django REST Framework (DRF)

### **AI**
- Google Gemini API (`google-generativeai`)

### **Frontend**
- HTML
- CSS
- JavaScript

### **Utilities**
- python-dotenv (for API keys)
- requests

### **Utilities**
- Other Modules and stacks

## 📷 Smart AI ToDo WebApplication

### 1️⃣ Dashboard 1(Home Page)
![Dashboard Screenshot 1](https://github.com/Vishlu/Smart_todo/blob/7ad95f3b1b06c414d755d76c2c699c4fe4e2751e/Screenshot%20(70).png)

### 2️⃣ Dashboard 2(filtered Page)
![Dashboard Screenshot 2](https://github.com/Vishlu/Smart_todo/blob/7ad95f3b1b06c414d755d76c2c699c4fe4e2751e/Screenshot%20(71).png)

### 3️⃣ Dashboard 3(filtered Page)
![Context Input Screenshot](https://github.com/Vishlu/Smart_todo/blob/7ad95f3b1b06c414d755d76c2c699c4fe4e2751e/Screenshot%20(72).png)

### 5️⃣ Task Form - Create/Edit Task
![Task List Screenshot](https://github.com/Vishlu/Smart_todo/blob/7ad95f3b1b06c414d755d76c2c699c4fe4e2751e/Screenshot%20(69).png)

### 4️⃣ Context Page
![AI Suggestion Screenshot](https://github.com/Vishlu/Smart_todo/blob/7ad95f3b1b06c414d755d76c2c699c4fe4e2751e/Screenshot%20(73).png)

---
Below is the context which you can use in this Web Applications for testing

| Context                                          |
| ------------------------------------------------ |
| Meeting with client tomorrow at 10 AM            |
| Submit project report to manager before deadline |
| Grocery shopping: milk, eggs, bread, fruits      |
| Fix API bug and deploy patch by Friday           |
| Respond to important email from HR               |
| Prepare presentation slides for Monday’s meeting |
I need to pay my electricity bill before Friday 5 pm
Finish reading AI research paper by next Sunday|


---

1️⃣ Setup Instructions
## ⚙️ Setup Instructions

### 1. Clone the Repository

git clone https://github.com/yourusername/smart-ai-todo.git
cd smart-ai-todo

2. Create a Virtual Environment
python -m venv virenv


Activate it:

Windows:

virenv\Scripts\activate


Mac/Linux:

source virenv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Set Environment Variables

Create a .env file in the root folder:

GEMINI_API_KEY=your_gemini_api_key_here

5. Run Migrations
python manage.py migrate

6. Create a Superuser (Optional for Admin)
python manage.py createsuperuser

7. Start the Development Server
python manage.py runserver


Visit http://127.0.0.1:8000/ in your browser.


---



## 📌 API Documentation

### Base URL


http://127.0.0.1:8000/api/


---

### **Tasks Endpoints**

| Method | Endpoint                     | Description                | Request Body (JSON) Example |
|--------|------------------------------|----------------------------|-----------------------------|
| GET    | `/tasks/`                     | List all tasks             | — |
| POST   | `/tasks/`                     | Create new task            | `{ "title": "My Task", "description": "Task details", "due_date": "2025-08-20", "category": "Work", "status": "Pending" }` |
| GET    | `/tasks/{id}/`                | Retrieve a specific task   | — |
| PUT    | `/tasks/{id}/`                | Update a task              | `{ "title": "Updated Task", "status": "Completed" }` |
| DELETE | `/tasks/{id}/`                | Delete a task              | — |

---

### **Context Endpoints**

| Method | Endpoint                     | Description                | Request Body (JSON) Example |
|--------|------------------------------|----------------------------|-----------------------------|
| GET    | `/contexts/`                  | List all context entries   | — |
| POST   | `/contexts/`                  | Add a context entry        | `{ "content": "Meeting with client tomorrow at 10 AM" }` |
| DELETE | `/contexts/{id}/delete/`      | Delete a context entry     | — |

---

### **AI Suggestion Endpoint**

| Method | Endpoint                     | Description                | Request Body (JSON) Example |
|--------|------------------------------|----------------------------|-----------------------------|
| POST   | `/tasks/ai-suggest/`          | Get AI-generated task data | `{ "title": "", "description": "", "context_ids": [1] }` |

📌 **Note:**  
- AI Suggestion will use the **most recent context** unless specific `context_ids` are passed.  
- If `title` and `description` are empty, AI will generate them from the context.
