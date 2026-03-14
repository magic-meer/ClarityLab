export async function POST(request) {
  try {
    const body = await request.json();
    const { question, model_name, generate_diagram, generate_image, generate_audio, generate_video, difficulty } = body;

    if (!question || question.trim().length < 5) {
      return Response.json(
        { status: "error", error: "Question must be at least 5 characters" },
        { status: 400 }
      );
    }

    const backendUrl =
      process.env.BACKEND_URL || "http://localhost:8000";

    const payload = { 
      question,
      difficulty: difficulty || "auto"
    };
    if (model_name) payload.model_name = model_name;
    if (generate_diagram !== undefined) payload.generate_diagram = generate_diagram;
    if (generate_image !== undefined) payload.generate_image = generate_image;
    if (generate_audio !== undefined) payload.generate_audio = generate_audio;
    if (generate_video !== undefined) payload.generate_video = generate_video;

    // Use step-by-step endpoint for better reliability
    const res = await fetch(`${backendUrl}/api/explain/steps`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      return Response.json(
        { status: "error", error: data.detail || "Backend error" },
        { status: res.status }
      );
    }

    return Response.json(data);
  } catch (error) {
    console.error("API proxy error:", error);
    return Response.json(
      { status: "error", error: "Failed to connect to AI engine. Make sure the Python backend is running on port 8000." },
      { status: 502 }
    );
  }
}
