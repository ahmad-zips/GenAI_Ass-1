# GenAI Studio
### Generative AI Image Restoration & Face-to-Sketch System

A unified web application implementing four deep-learning tasks through a single browser-based interface.

The system provides image restoration, corruption-aware routing, soft Mixture-of-Experts restoration, and face-to-sketch generation. All trained models are integrated into the application using **ONNX Runtime** and the complete system runs through **Docker**.

---

## ✨ Features

| Task | Description |
|---|---|
| **Task 1 — Universal Restoration** | Restores images affected by different types of synthetic corruption using a single universal restoration model. |
| **Task 2 — Hard-Routed Restoration** | Classifies the input corruption and routes the image to the corresponding specialist restoration model. |
| **Task 3 — Soft Mixture-of-Experts** | Uses a learned gating mechanism to combine the outputs of multiple restoration specialists. |
| **Task 4 — Face-to-Sketch** | Generates sketch-style images from input face images using a conditional generative model. |

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │    React Frontend   │
                    │     Web Interface   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │       Backend       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    ONNX Runtime     │
                    │   Trained Models    │
                    └─────────────────────┘

              Everything runs inside Docker containers.
```

### Technology Stack

- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** FastAPI, Python
- **Inference:** ONNX Runtime
- **Deployment:** Docker & Docker Compose
- **Models:** PyTorch-trained models exported to ONNX

---

## 🚀 Running the Application

### Requirements

- Docker Desktop
- Git
- Git LFS

### 1. Clone the repository

```bash
git clone <repository-url>
cd GenAI_Ass-1
```

### 2. Start the application

```bash
docker compose up --build
```

### 3. Open the application

Open:

```text
http://localhost:3000
```

The frontend communicates with the FastAPI backend automatically through the Dockerized nginx configuration.

---

## 🤖 Models

The repository contains the trained ONNX inference models required by the application.

The models are tracked using **Git LFS** because of their size.

The application includes:

```text
models/
├── task1_universal.onnx
├── task2_classifier.onnx
├── task2_specialist_gaussian_blur.onnx
├── task2_specialist_occlusion.onnx
├── task2_specialist_salt_pepper.onnx
├── task3_soft_moe.onnx
└── task4_generator.onnx
```

No model training is required to run the deployed application.

---

## 📡 API Endpoints

| Method | Endpoint | Task |
|---|---|---|
| `GET` | `/api/health` | Backend and model health status |
| `POST` | `/api/restore/universal` | Task 1 — Universal Restoration |
| `POST` | `/api/restore/hard` | Task 2 — Hard-Routed Restoration |
| `POST` | `/api/restore/soft` | Task 3 — Soft MoE Restoration |
| `POST` | `/api/sketch` | Task 4 — Face-to-Sketch |

---

## 🧪 Corruption Types

The restoration tasks support:

- Salt-and-pepper noise
- Gaussian blur
- Occlusion
- Already-corrupted input

The application provides predefined corruption severity levels and corresponding restoration workflows.

---

## 📁 Project Structure

```text
GenAI_Ass-1/
│
├── backend/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── models/
│   ├── task1_universal.onnx
│   ├── task2_classifier.onnx
│   ├── task2_specialist_gaussian_blur.onnx
│   ├── task2_specialist_occlusion.onnx
│   ├── task2_specialist_salt_pepper.onnx
│   ├── task3_soft_moe.onnx
│   └── task4_generator.onnx
│
├── scripts/
├── tools/
├── docker-compose.yml
├── .gitattributes
├── .gitignore
└── README.md
```

---

## 📌 Project Status

**Complete and deployable.**

All four assignment tasks are integrated into a single browser-based application and can be executed through the provided Docker setup.

The application is designed so that model inference is performed locally through ONNX Runtime rather than requiring a separate training environment.

---

## 👥 Author

**Zibyah Ahmad**  

Developed as part of the Generative AI coursework.