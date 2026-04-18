# 🐍 Snake Game – Fullscreen Edition

**Snake Game** is a modernized version of the classic snake game built with **Python** and **Pygame**.  
It features multiple game modes, fullscreen scaling, and smooth animations for an engaging experience on any screen size.

---

## 🎮 How to Play

- **Move**: Use the **Arrow Keys** to control the snake.
- **Eat Food**: Grow your snake by eating the food items.
- **Avoid Collisions**: Don’t crash into yourself or the walls (in certain modes).
- **Game Modes**:
  - **Classic**: Standard snake gameplay.
  - **Timed**: Eat as much as you can before time runs out.
  - **Hardcore**: Faster snake, less reaction time.
  - **Zen**: Relaxed mode without game over conditions.
  - **Survival**: Limited lives, try to last as long as possible.

---

## 📦 Installation Instructions

### ✅ Step 1: Download or Clone the Repository

#### Option A: Download ZIP
1. Click the green **"Code"** button at the top of this GitHub page.
2. Select **"Download ZIP"**.
3. Extract the ZIP file to any folder.

#### Option B: Clone via Git
```bash
git clone https://github.com/rajat-bhootra/snake-game.git
cd snake-game
```
### ✅ Step 2: Install Python and Pygame

Make sure Python 3.7 or higher is installed on your system.
You can check using:
```bash
python --version
```
Then install pygame:
```bash
pip install pygame
```
---
## ▶️ How to Run the Game
1. Open a terminal or command prompt.
2. Navigate to the project folder where snake_game.py is located.
3. Run the game:
```bash
python3 zombie_shooter.py
```
---
## 📁 Required Files and Folders
Make sure all the following are present in the same folder:
```css
snake-game/
│
├── snake_game.py          # Main game script
├── main.py                # Web entry script for pygbag build
├── assets/                # Folder containing images & sounds
│   ├── image/
│   │   ├── snake_head.png
│   │   ├── snake_body.png
│   │   ├── snake_tail.png
│   │   ├── apple.png
│   │   ├── background.png
│   │   └── ...
│   └── sound/
│       ├── eat.mp3
│       ├── game_over.mp3
│       └── ...
└── README.md              # Project documentation
```

---

## 🌐 Play Online (Web Build)

You can host this game online using **Pygbag** + **GitHub Pages**.

### 1) Build locally for browser

Install pygbag:

```bash
pip install pygbag
```

From the project root, run:

```bash
python -m pygbag --build --ume_block 0 --app_name SnakeGame .
```

Web files will be generated in:

```bash
build/web
```

### 2) Deploy automatically with GitHub Actions

This repository includes:

- `.github/workflows/deploy-web.yml`

Steps:

1. Push your code to GitHub.
2. In repository settings, enable **GitHub Pages** source as **GitHub Actions**.
3. Push to `main` (or run workflow manually).
4. The workflow builds web files and deploys them to GitHub Pages.

### Web Notes

- Browser build uses fixed window size (no forced fullscreen).
- High scores are kept in memory for web sessions.
- Audio starts only after user interaction (browser policy).

