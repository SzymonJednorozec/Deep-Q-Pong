# Deep-Q-Pong 🏓
 
An autonomous AI agent trained to play Pong from scratch using Reinforcement Learning.
 
---
 
## 🎯 Project Overview
 
This project features a custom-built Pong environment and an AI agent powered by a **Deep Q-Network (DQN)**. This environment was developed from the ground up to allow for granular control over physics, state representation, and reward shaping.
 
---
 
## 🚀 Key Features
 
- **Custom Game Engine**  Built with `Pygame`, optimized for high-speed training.
- **Double DQN (DDQN)**  Mitigates overestimation bias by decoupling action selection from evaluation.
- **Optimized Performance**  Fully vectorized Bellman equation implementation using `PyTorch` and `NumPy`.
 
---
 
## 🧠 The AI 
 
The agent perceives the world through a **5-dimensional state vector:**
 
| # | Input |
|---|---|
| 1 | Paddle Y-position |
| 2 | Ball X-position |
| 3 | Ball Y-position |
| 4 | Ball Velocity X |
| 5 | Ball Velocity Y |
  
---
 
## 📊 Visualizing Results
 
The project includes a real-time plotting tool (`Matplotlib`) to monitor:
 
- **Score per Game**  Individual performance
- **Mean Score**  Rolling average to track long-term learning
- **Epsilon Decay**  Visualizing the shift from exploration to exploitation
 
---
 
## 🛠️ Tech Stack
 
| Category | Technology |
|---|---|
| **Language** | Python 3.12 |
| **ML Framework** | PyTorch |
| **Graphics** | Pygame |
| **Analysis** | Matplotlib, NumPy |
| **Deployment** | ONNX, Streamlit (via Neuro-Policy-Mapper) |
 
---
 
## 🏗️ Installation & Usage
 
 
### 1. Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### 2. Run training
 
```bash
python agent.py
```