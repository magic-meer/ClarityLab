export async function POST(request) {
  try {
    const formData = await request.formData();
    const question = formData.get("question");
    const context = formData.get("context");
    const model_name = formData.get("model_name");
    const file = formData.get("file");
    const generate_diagram = formData.get("generate_diagram");
    const generate_image = formData.get("generate_image");
    const generate_audio = formData.get("generate_audio");

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

    // Build backend FormData with all fields
    const backendForm = new FormData();
    backendForm.append("file", file);
    backendForm.append("question", question);
    if (context) backendForm.append("context", context);
    if (model_name) backendForm.append("model_name", model_name);
    if (generate_diagram !== null && generate_diagram !== undefined) backendForm.append("generate_diagram", generate_diagram);
    if (generate_image !== null && generate_image !== undefined) backendForm.append("generate_image", generate_image);
    if (generate_audio !== null && generate_audio !== undefined) backendForm.append("generate_audio", generate_audio);

    const res = await fetch(
      `${backendUrl}/api/analyze-image`,
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
