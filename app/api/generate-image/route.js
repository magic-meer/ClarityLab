export async function POST(request) {
  try {
    const body = await request.json();
    const { prompt, model_name } = body;

    if (!prompt || prompt.length < 3) {
      return Response.json(
        { status: "error", error: "Prompt must be at least 3 characters" },
        { status: 400 }
      );
    }

    const backendUrl =
      process.env.BACKEND_URL || "http://localhost:8080";

    const res = await fetch(`${backendUrl}/api/generate-image`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt, model_name }),
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
    console.error("Image generation API Proxy error:", error);
    return Response.json(
      { status: "error", error: "Failed to connect to AI engine." },
      { status: 502 }
    );
  }
}
