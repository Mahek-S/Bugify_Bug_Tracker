# Bugify - Bug Tracker

Bugify is a web-based Bug Tracking System that helps manage bugs efficiently. The project implements a **backend with FastAPI + MongoDB**, a **frontend with HTML, CSS, and JavaScript**, and a **CI/CD pipeline** using **GitHub Actions**.

---

## Features

**Frontend:**  
- HTML, CSS, JavaScript interface  
- User authentication (LocalStorage-based)  
- Role-based access (Admin/User)  
- Dashboard with search and filters  

**Backend:**  
- FastAPI REST APIs  
- MongoDB database integration  
- Authentication using JWT & password hashing  
- Automated unit and integration tests using pytest  

**Testing:**  
- Backend: automated tests with pytest  
- Frontend: manual unit & integration verification  
- System & End-to-End testing: complete application workflows tested manually  

**CI/CD Pipeline:**  
- Backend CI: runs automated tests and validates FastAPI startup  
- Frontend CI: runs ESLint and requires manual verification  
- Ensures stable, production-ready builds and safe merges  

---

## Tech Stack

| Layer       | Technology                       |
|------------|----------------------------------|
| Frontend   | HTML, CSS, JavaScript            |
| Backend    | FastAPI, MongoDB                 |
| Testing    | Pytest (backend), Manual (frontend) |
| CI/CD      | GitHub Actions (backend tests + ESLint frontend) |

---

## Author

**Mahek S.**  
Software Development Lifecycle Project — CI Testing for Web Applications