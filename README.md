# CodeAcharya — AI Coding Mentor
### An Intelligent Personalized Programming Learning and Debugging Platform

> **"Instead of simply generating solutions, CodeAcharya analyzes a student's code, identifies errors and misconceptions, provides progressive hints, recommends suitable coding problems, tracks learning progress, and conducts AI-powered viva sessions."**

---

## 🌟 System Architecture & Key Features

### 1. Browser-Based Code IDE (Monaco Editor)
- High-performance Monaco code editor supporting **Python**, **C**, **C++**, and **Java**.
- Real-time syntax highlighting, custom test case execution, and automated test runners with timing analysis.

### 2. AST-Powered Static Code Analysis
- Evaluates code structure via Python Abstract Syntax Tree (`ast` module) and static inspectors.
- Automatically checks for:
  - **Base case conditions in recursive functions** (e.g. identifies zero-multiplication collapse in factorial).
  - **Loop nesting complexity estimation** ($O(1)$, $O(N)$, $O(N^2)$, $O(2^N)$ branching recursion).
  - **Infinite loop hazard detection** (`while True` loops lacking termination).
  - **Code execution security guards**.

### 3. Socratic Progressive Hint System
Guided problem solving that avoids immediately handing over the answer:
- **Level 1 — Conceptual:** Prompts understanding of foundational principles and input domain.
- **Level 2 — Algorithmic:** Directs focus toward specific data structures or decision branches.
- **Level 3 — Structural:** Provides concrete mathematical or invariant rules.
- **Level 4 — Resolution:** Step-by-step walkthrough of the computational logic.
- Self-check reflective questions for student cognitive retention.

### 4. AI Viva Voce Mode (Oral Defense Simulation)
- Acts as a University Computer Science Viva Examiner evaluating the student's actual code.
- Generates 4 rigorous questions spanning:
  1. *Conceptual Depth*
  2. *Code Architecture & Data Structure Choices*
  3. *Big-O Time & Space Complexity Proofs*
  4. *Edge Cases & Failure Modes*
- **Speech Synthesis & Speech Recognition:** Examiner speaks questions aloud; students can dictate or type responses.
- **Multi-Metric Scorecard:**
  - Conceptual Understanding (%)
  - Code Understanding (%)
  - Complexity Analysis (%)
  - Communication Score (%)
  - Overall Grade & Qualitative Examiner Remarks

### 5. Student Skill Profile & Coding Analytics
- **Topic Mastery Matrix:** Tracks proficiency across Recursion, Arrays, Stack, Dynamic Programming, Algorithms, and Strings.
- **Analytics KPIs:** Problems Solved, Total Submissions, Hints Unlocked, and Active Debugging Time.
- **Misconception & Bug Log:** Identifies persistent conceptual errors.
- **AI Weekly Learning Report:** Summarizes growth areas and oral defense readiness.

### 6. Adaptive Problem Recommendations
- Recommends tailored practice problems targeted at the student's lowest scored mastery areas.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Start the FastAPI Backend
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API documentation is available at: `http://127.0.0.1:8000/docs`

### 2. Start the React Frontend
```bash
cd frontend
npm install
npm run dev
```
Open your browser to: `http://localhost:5173/`

---

## ⚙️ AI Configuration
- **BharatCode API:** CodeAcharya is integrated with the **BharatCode API** (`https://bharatcode.ai/api/model/v1`) for dynamic AI coding problem generation, progressive Socratic hints, algorithmic debugging guidance, and automated AI viva voce defense.
- **Environment Setup:** Configure your BharatCode API credentials in `backend/.env`:
  ```env
  BHARATCODE_API_KEY=your_bharatcode_api_key
  BHARATCODE_BASE_URL=https://bharatcode.ai/api/model/v1
  BHARATCODE_MODEL=qwen-3.8-27b
  ```
- **Deterministic Offline Fallback:** If `BHARATCODE_API_KEY` is not set or network is unavailable, CodeAcharya automatically operates using its built-in Deterministic Blueprint Engine across 8 algorithmic topics with 245+ verified problems, multi-language starter code, and progressive Socratic hints.
