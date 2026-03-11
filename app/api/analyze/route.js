export async function POST(request) {
  try {
    const formData = await request.formData();
    const question = formData.get("question");
    const context = formData.get("context");
    const model_name = formData.get("model_name");
    const file = formData.get("file");

    if (!question || question.trim().length < 5) {
      return Response.json(
        { status: "error", error: "Question must be at least 5 characters" },
        { status: 400 }
      );
    }

    if (!file) {
      return Response.json(
        { status: "error", error: "An image file is required" },
        { status: 400 }
      );
    }

    const backendUrl =
      process.env.BACKEND_URL || "http://localhost:8000";

    const params = new URLSearchParams({ question });
    if (context) params.append("context", context);
    if (model_name) params.append("model_name", model_name);

    const backendForm = new FormData();
    backendForm.append("file", file);

    const res = await fetch(
      `${backendUrl}/api/analyze-image?${params.toString()}`,
      { method: "POST", body: backendForm }
    );

    const data = await res.json();

    if (!res.ok) {
      return Response.json(
        { status: "error", error: data.detail || "Backend error" },
        { status: res.status }
      );
    }

    return Response.json(data);
  } catch (error) {
    console.error("Image analysis proxy error:", error);
    return Response.json(
      { status: "error", error: "Failed to connect to AI engine." },
      { status: 502 }
    );
  }
}
