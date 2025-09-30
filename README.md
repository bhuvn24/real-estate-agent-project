# Real Estate Virtual Agent

A proof-of-concept multi-agent system that simulates a conversation with an intelligent real estate consultant. This application uses a 3D avatar, voice recognition, and a backend powered by specialized AI agents to recommend properties, negotiate prices, and send follow-ups.

---

## Features

-   **🤖 Multi-Agent System:** An orchestrator manages several specialized agents, each with a single responsibility:
    -   **Greeting Agent:** Uses Google's Gemini API for natural, conversational greetings.
    -   **Recommendation Agent:** Filters and suggests properties based on user preferences.
    -   **Emotion Agent:** Performs basic sentiment analysis to gauge user interest.
    -   **Negotiation Agent:** Adjusts property prices based on user interest and other factors.
    -   **Finance Agent:** Calculates loan and EMI options for a given property.
    -   **Follow-Up Agent:** Sends a summary via WhatsApp using the Twilio API.
-   **🗣️ Voice Interaction:** Leverages the browser's Web Speech API for both speech-to-text (user input) and text-to-speech (agent responses).
-   **🎨 Interactive 3D Avatar:** A simple, interactive 3D avatar built with React Three Fiber provides a visual front for the agent.
-   **⚡ Real-time Communication:** Uses WebSockets for low-latency communication between the frontend and the backend agents.

---

## Tech Stack

-   **Backend:**
    -   🐍 **Python**
    -   **Flask** & **Flask-SocketIO**
    -   **Google Gemini API** for generative AI
    -   **Twilio API** for WhatsApp messaging
    -   **Pandas** for data handling
-   **Frontend:**
    -   ⚛️ **React**
    -   **React Three Fiber** & **Drei** for 3D graphics
    -   **Socket.IO Client** for WebSocket communication
    -   **Web Speech API** (built into modern browsers)

---

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   **Python** (3.8 or newer)
-   **Node.js and npm**
-   **Git**
-   API Keys for:
    -   **Google Gemini**
    -   **Twilio**

---

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/real-estate-agent.git](https://github.com/your-username/real-estate-agent.git)
    cd real-estate-agent
    ```

2.  **Backend Setup:**
    ```sh
    # Navigate to the backend directory
    cd backend

    # Create and activate a virtual environment
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On Mac/Linux:
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt
    ```

3.  **Frontend Setup:**
    ```sh
    # Navigate to the frontend directory from the root
    cd frontend

    # Install npm packages
    npm install
    ```

---

### Configuration

The backend requires API keys to function.

1.  In the `backend` folder, create a new file named `.env`.
2.  Copy the contents of `.env.example` (or the block below) into your new `.env` file.
3.  Replace the placeholder values with your actual API keys.

**`.env` file contents:**
