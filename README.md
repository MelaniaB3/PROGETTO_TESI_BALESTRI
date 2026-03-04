Capitalizing Tacit Knowledge: An AI Conversational Framework for Industrial Maintenance
🚀 UX Research & AI-Augmented Prototyping
This repository contains the technical infrastructure and datasets developed for my Master’s Thesis in Communication Strategies & Techniques. The project focuses on bridging the "Information Asymmetry" in industrial maintenance through an advanced Conversational AI Assistant.
📌 Project Overview
In industrial environments, expert technicians possess valuable tacit knowledge (the "Expert Tricks") that is systematically lost during manual reporting. This leads to the "Double-Trip Syndrome": repeated visits due to poor initial diagnostic data.
The Solution: A structured Conversational AI designed to conduct "debriefing interviews" using 8D/Root Cause Analysis (RCA) methodologies to extract and digitize high-value technical insights.
🧠 Core Features
Multi-Agent Simulation: A Python-based environment where two LLMs interact (Agent 1: Simulated Technician vs. Agent 2: AI Assistant).
Behavioral Archetypes: Stress-testing the conversation logic against 4 distinct user profiles (Collaborative, Reluctant, Unstructured, and Technical Purist).
Iterative Prompt Engineering: Evolution of 5 different prompting strategies (Approaches A to E) to find the optimal balance between procedural rigor and conversational fluidity.
LLM-as-a-Judge: An automated evaluation pipeline using Gemini Pro to score 324 interactions across custom UX metrics.
📂 Repository Structure
The project is divided into two main functional modules:
1. 🤖 Generation Module (/generazione_conversazioni)
Contains the scripts to run the multi-agent simulations.
run_A.py, run_B.py, run_C.py: Initial test scripts for basic prompting philosophies.
run_D_E.py: The final optimized "Hybrid Prompt" logic (The Winner).
config_matrix.json: The experimental matrix defining scenarios and archetypes.
2. ⚖️ Evaluation Module (/valutazione_conversazioni)
Contains the infrastructure for the automated analysis.
vault.py: The "Judge Agent" script that processes conversation logs.
evaluation_rubric/: Detailed metrics and scoring criteria used by the AI Judge.
🛠 Tech Stack
Language: Python
AI Models: Google Gemini 2.5 Flash Lite (Generation) & Gemini Pro (Evaluation)
Frameworks: Pydantic (Data Validation), Itertools (Matrix Generation)
Workflow: AI-Augmented Development. I leveraged LLMs to assist in the programming and debugging of this simulation environment, focusing on high-level conversational architecture and data structure.
📊 Key Results
97.22% Success Rate achieved with Approach E (Hybrid Design + High-Reasoning Model).
17% Efficiency Gain in conversational turns compared to baseline models.
Structured Output: Every conversation results in a structured JSON file, ready for corporate CRM integration.
📄 Final Note
This project demonstrates how Conversational UX is a synergy between Human-Centered Design and Computational Reasoning. By engineering the logic and stress-testing the behavior, we can transform "silent" expertise into a strategic digital asset.
