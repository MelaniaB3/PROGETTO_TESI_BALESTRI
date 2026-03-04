# Capitalizing Tacit Knowledge: An AI Conversational Framework for Industrial Maintenance

### 🚀 Applied UX Research & AI-Augmented Prototyping
*A Master’s Thesis project focused on bridging the "Information Asymmetry" through structured AI-driven debriefings.*

---

## 📌 01. Project Overview
In high-tech industrial maintenance, senior technicians possess **tacit knowledge** ("expert tricks") that is rarely documented. Current reporting is often shallow, leading to the **"Double-Trip Syndrome"**: repeated visits due to poor diagnostic data.

**The Mission:** I designed a **Conversational AI Assistant** that interviews technicians post-intervention, using **Root Cause Analysis (RCA)** methodologies to transform natural speech into strategic digital assets.

---

## 🧠 02. Methodology & Design Strategies

### 👥 Behavioral Archetypes (Stress-Testing)
To ensure system robustness, the conversational logic was validated against 4 simulated user profiles:
*   **The Collaborative Expert:** Detailed and structured (Benchmark).
*   **The Reluctant Veteran:** Minimalist and skeptical (Testing proactive elicitation).
*   **The Unstructured Technician:** Vague and disorganized (Testing cognitive scaffolding).
*   **The Technical Purist:** Hyper-accurate and jargon-heavy (Testing lexical adaptation).

### ✍️ Prompt Engineering Evolution
The project involved an iterative design of 5 prompting strategies:
*   **Approaches A, B, C:** Testing Procedural, Outcome-led, and Few-Shot philosophies.
*   **Approach D:** Implementation of a "Hybrid Prompt" on a standard model.
*   **Approach E (Winner):** The "Hybrid Prompt" paired with high-level reasoning models, achieving a **97.22% Success Rate**.

---

## 🛠 03. Technical Implementation

### 🤖 Multi-Agent Simulation Environment
I developed a functional testing infrastructure in **Python** using an **AI-augmented coding workflow**.
*   **Twin-Agent Setup:** A simulated interaction between a "Technician Agent" and an "Assistant Agent".
*   **324 Interactions:** A large-scale automated stress-test matrix covering various failure scenarios and information gaps.

### ⚖️ LLM-as-a-Judge Evaluation
To eliminate human bias, I engineered an automated evaluation pipeline:
*   **Judge Agent:** Powered by Gemini Pro with specific UX metrics.
*   **Logic Tracing:** Used **Chain-of-Thought (CoT)** reasoning to provide a logical justification for every score assigned.

---

## 📂 04. Repository Structure

### 📁 `generazione_conversazioni/`
Contains the core simulation logic.
*   `run_A.py`, `run_B.py`, `run_C.py`: Scripts for initial baseline testing.
*   **`run_D_E.py`**: The production-ready script for the final optimized Hybrid logic.
*   `config_matrix.json`: The experimental matrix defining the 324 unique test cases.

### 📁 `valutazione_conversazioni/`
The automated analysis engine.
*   `vault.py`: The "Judge" script that processes logs and calculates performance metrics.
*   `data_outputs/`: (Where stored) Structured JSON and CSV logs for quantitative analysis.

---

## 📊 05. Key Results & UX Impact

*   **+44% Diagnostic Success:** Compared to traditional rule-based prompting.
*   **+47% Protocol Adherence:** Near-perfect execution of the 8D/RCA methodology (4.83/5).
*   **17% Efficiency Gain:** Significant reduction in conversational turns without information loss.
*   **Interdependency Discovery:** Proved that high-fidelity Conversational UX requires a precise alignment between **Prompt Architecture** and **Computational Reasoning Power**.

---

## 💻 06. Tech Stack
*   **Language:** Python
*   **Models:** Google Gemini 2.5 Flash Lite & Gemini Pro
*   **Data Formats:** JSON (Logs), CSV (Analysis)
*   **Validation Frameworks:** Pydantic

---

## ✉️ 07. Contacts & Links
*   **UX Designer:** Melania Balestri
*   **Full Case Study:** [Link to your Portfolio]
*   **LinkedIn:** [Link to your LinkedIn]

---
*Developed as part of the Master’s Degree in Communication Strategies & Techniques - University of Siena.*
