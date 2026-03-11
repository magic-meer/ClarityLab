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
      process.env.BACKEND_URL || "http://localhost:8000";

    const backendParams = new URLSearchParams({ prompt });
    if (model_name) backendParams.append("model_name", model_name);

    const res = await fetch(`${backendUrl}/api/generate-image?${backendParams.toString()}`, {
      method: "POST",
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
