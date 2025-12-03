# Motilal Oswal Algo Trading Engine

A high-performance, modular Python middleware for the Motilal Oswal Trading API. Built with **FastAPI**, this application acts as a bridge to execute algorithmic trades across multiple exchanges (NSE, BSE, MCX, NFO, CDS).

## 🚀 Features

*   **Multi-Exchange Support:** Unified logic for NSE, BSE, NSEFO, BSEFO, MCX, and Currency (CDS).
*   **Automatic Instrument Mapping:** Downloads and caches Scrip Masters automatically to map symbols (e.g., "GOLDPETAL") to internal tokens.
*   **Smart Quantity Logic:** Auto-calculates lot sizes for derivatives.
*   **Full API Coverage:**
    *   Place, Modify, Cancel Orders.
    *   Fetch Order Book, Trade Book, Positions, and Holdings.
    *   Get Live LTP and Margin Summaries.
*   **Security:** Implements TOTP (2FA) generation and strictly follows MOFSL header requirements (IP/MAC address binding).
*   **Modular Architecture:** Clean separation of concerns (Models, Backend, Routes).

## 📂 Project Structure

```text
mofsl_algo/
├── main.py          # Entry point (FastAPI Routes)
├── backend.py       # Core logic (MOFSL API communication)
├── models.py        # Pydantic data models (Request bodies)
├── utils.py         # Helper functions (Public IP, MAC)
├── config.py        # Configuration constants
├── requirements.txt # Python dependencies
└── README.md        # Documentation

🛠️ Installation
Clone the repository:
code
Bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
Create a Virtual Environment:
code
Bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
Install Dependencies:
code
Bash
pip install -r requirements.txt
⚡ Usage
Start the Server:
code
Bash
python main.py
# OR for auto-reload
uvicorn main:app --reload
Access the API:
The server will start at http://127.0.0.1:8000.
API Documentation (Swagger UI):
Visit http://127.0.0.1:8000/docs in your browser to test endpoints interactively.
🔗 Key Endpoints
Method	Endpoint	Description
POST	/validate_motilal	Login & Download Instruments
POST	/place_order_motilal	Place Order (Any Exchange)
POST	/modify_order_motilal	Modify Pending Order
POST	/get_positions	Get Net Positions
POST	/get_ltp	Get Live Price
⚠️ Disclaimer
This software is for educational purposes only. Algorithmic trading involves financial risk. The developers of this repository are not responsible for any financial losses incurred while using this code. Ensure you test thoroughly in a controlled environment before using real funds.
code
Code
---

### 3. How to Push to GitHub (Step-by-Step)

Since you already had a `venv` issue, make sure you are in the correct folder: `mosfl_algo`.

**Step 1: Create the Repo on GitHub**
1.  Go to [GitHub.com](https://github.com).
2.  Click the **+** icon (top right) -> **New repository**.
3.  **Repository name:** (Use one from section 1, e.g., `mofsl-algo-fastapi`).
4.  **Description:** "Motilal Oswal Trading API integration using FastAPI."
5.  **Public/Private:** Choose Private (recommended if you have personal keys) or Public.
6.  **Do NOT** check "Add a README", "Add .gitignore". (We already made them locally).
7.  Click **Create repository**.

**Step 2: Connect and Push from VS Code Terminal**
Run these commands one by one inside your VS Code terminal (ensure your terminal is inside the `mosfl_algo` folder).

1.  **Initialize Git:**
    ```bash
    git init
    ```

2.  **Add all files:**
    *(This will use your `.gitignore` to safely skip the `venv` folder)*
    ```bash
    git add .
    ```

3.  **Commit the files:**
    ```bash
    git commit -m "Initial commit: Modular MOFSL Algo structure"
    ```

4.  **Rename branch to main (Standard practice):**
    ```bash
    git branch -M main
    ```

5.  **Link to GitHub:**
    *(Replace the URL below with the one you got in Step 1)*
    ```bash
    git remote add origin https://github.com/YOUR_GITHUB_USERNAME/mofsl-algo-fastapi.git
    ```

6.  **Push the code:**
    ```bash
    git push -u origin main
    ```

**Success!** Your code is now safely on GitHub with professional documentation.
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
You need to keep the README.md file in the Main Folder (Root Directory) of your project.
It should sit right next to main.py, requirements.txt, and .gitignore.
Step-by-Step Guide (Using VS Code)
Open VS Code and make sure you are looking at your mosfl_algo folder on the left sidebar.
Right-click in the empty space of the sidebar (or click the "New File" icon with a + sign next to the folder name).
Name the file exactly: README.md
Note: It must be all capital letters for "README" and lowercase ".md".
Paste the long code block I gave you in the previous response into this file.
Save the file (Ctrl + S).
How it should look in your VS Code Explorer:
code
Text
mosfl_algo/
├── .gitignore
├── venv/
├── backend.py
├── config.py
├── main.py
├── models.py
├── README.md       
├── requirements.txt
└── utils.py
How to push this new file to Git?
Since you just created a new file, Git doesn't know about it yet. You need to tell Git to track it.
Run these 3 commands in your VS Code Terminal:
code
Bash
# 1. Add the new file to the staging area
git add README.md

# 2. Save (Commit) the change
git commit -m "Added README documentation"

# 3. Send it to GitHub
git push
Now, when you visit your repository link on GitHub, you will see that beautiful documentation displayed on the front page!
Model
ThinkingThoughts
Expand to view model thoughts

chevron_right
Here is the complete content for your README.md file. Copy the code block below and paste it into your README.md file.
code
Markdown
# Motilal Oswal FastAPI Integration

A professional, modular middleware for the Motilal Oswal (MOFSL) Trading API. This project uses **FastAPI** to create a robust bridge for algorithmic trading, supporting multiple exchanges, automatic instrument mapping, and 2FA authentication.

## 🚀 Features

*   **Multi-Exchange Support:** Unified execution for NSE, BSE, MCX, NSEFO, BSEFO, and CDS (Currency).
*   **Smart Instrument Mapping:** Automatically downloads and caches Scrip Master CSVs to map human-readable symbols (e.g., "NIFTY", "GOLD") to internal tokens.
*   **Intelligent Logic:** Auto-calculates lot sizes for F&O and currency orders.
*   **Security:** Built-in TOTP generation for 2FA and strict header compliance (IP/MAC binding).
*   **Modular Design:** Clean separation of API routes, backend logic, and data models.
*   **Full API Coverage:** 
    *   Place, Modify, Cancel Orders.
    *   Live LTP (Last Traded Price).
    *   Fetch Order Book, Trade Book, Positions, Holdings, and Margin limits.

## 📂 Project Structure

```text
MOTILAL-OSWAL-FASTAPI-INTEGRATION/
├── main.py          # Entry point (FastAPI Routes)
├── backend.py       # Core logic (MOFSL API communication)
├── models.py        # Pydantic data models (Request/Response schemas)
├── utils.py         # Helper functions (Public IP, MAC Address)
├── config.py        # Configuration constants and URLs
├── requirements.txt # Python dependencies
└── README.md        # Project Documentation
🛠️ Installation
Clone the repository:
code
Bash
git clone https://github.com/YOUR_USERNAME/MOTILAL-OSWAL-FASTAPI-INTEGRATION.git
cd MOTILAL-OSWAL-FASTAPI-INTEGRATION
Create a Virtual Environment:
code
Bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
Install Dependencies:
code
Bash
pip install -r requirements.txt
⚡ Usage
Start the Server:
code
Bash
python main.py
# OR for auto-reload during development
uvicorn main:app --reload
Access the API:
The server will start at http://127.0.0.1:8000.
Interactive Documentation:
Visit http://127.0.0.1:8000/docs to test endpoints directly via Swagger UI.
🔗 Key Endpoints
Method	Endpoint	Description
POST	/validate_motilal	Login & Download Instrument Masters
POST	/place_order_motilal	Place Order (Auto-detects exchange logic)
POST	/modify_order_motilal	Modify an existing order
POST	/cancel_order_motilal	Cancel an order
POST	/get_positions	Get current open positions
POST	/get_ltp	Get Live Price for any scrip
POST	/get_margin_summary	Check available funds
⚠️ Disclaimer
This software is provided for educational purposes only. Algorithmic trading involves significant financial risk. The developers of this repository are not responsible for any financial losses incurred while using this code. Always test strategies in a controlled environment before using real funds.