# System Architecture

You can copy the Mermaid code below and paste it into Draw.io (using **Arrange > Insert > Advanced > Mermaid**) or view it using any Markdown previewer that supports Mermaid.js.

```mermaid
flowchart TB
    %% Entities
    User((User))
    
    %% Frontend (Next.js)
    subgraph Frontend [Next.js 15 Frontend Client]
        UI[Chat UI & Components]
        TTS[Native SpeechSynthesis TTS]
        Render[Markdown & Mermaid Renderer]
    end

    %% Backend (FastAPI)
    subgraph Backend [FastAPI AI Engine Orchestrator]
        API[API Routes /api/*]
        Planner[Reasoning Generator]
        TextGen[Text Explanation Generator]
        VisGen[MultiModal Asset Handler]
        
        API --> Planner
        Planner --> TextGen
        Planner --> VisGen
    end

    %% Vertex AI / GCP Ecosystem
    subgraph GCP [Google Cloud Vertex AI]
        Gemini[Gemini 2.x Models]
        Imagen[Imagen 3.0]
        Veo[Veo 2.0 Video Gen]
    end
    
    %% Connections
    User == "Prompts & Toggles" ==> UI
    UI == "REST API Calls" ==> API
    UI -. "Reads Aloud" .-> TTS
    
    %% Backend to Cloud calls
    TextGen == "Generate Content" ==> Gemini
    VisGen == "Diagram Prompts" ==> Gemini
    VisGen == "Image Prompts" ==> Imagen
    VisGen == "Video Prompts" ==> Veo
    
    %% Responses
    Gemini -. "Mermaid/Text Data" .-> API
    Imagen -. "Base64 Image" .-> API
    Veo -. "Base64 Video" .-> API
    
    API -. "Streaming / JSON Response" .-> Render
    Render -. "Displays Multimedia" .-> User

    %% Styling Elements
    classDef client fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef be fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef cloud fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    
    class UI,TTS,Render client;
    class API,Planner,TextGen,VisGen be;
    class Gemini,Imagen,Veo cloud;
```
