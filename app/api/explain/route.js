export async function POST(request) {
  try {
    const body = await request.json();
    const { question, difficulty } = body;

    if (!question || question.trim().length < 5) {
      return Response.json(
        { status: "error", error: "Question must be at least 5 characters" },
        { status: 400 }
      );
    }

    const backendUrl =
      process.env.BACKEND_URL || "http://localhost:8000";

    const res = await fetch(`${backendUrl}/api/explain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, difficulty: difficulty || "beginner" }),
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
