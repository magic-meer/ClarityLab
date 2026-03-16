export async function POST(request) {
  const startTime = Date.now();
  let topicPreview = "Unknown";

  try {
    const body = await request.json();
    topicPreview = body.prompt ? body.prompt.slice(0, 50) : "No Prompt";
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8080";

    console.log(`[PROXY] Requesting text explanation for: "${topicPreview}"`);

    const res = await fetch(`${backendUrl}/api/generate-explanation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const duration = (Date.now() - startTime) / 1000;
    const data = await res.json();

    if (!res.ok) {
      console.error(`[PROXY] Explanation Backend Error (${res.status}) after ${duration.toFixed(1)}s:`, data);
      return Response.json(
        { status: "error", error: data.detail || data.error || "Backend error" },
        { status: res.status }
      );
    }

    console.log(`[PROXY] Explanation SUCCESS for "${topicPreview}" in ${duration.toFixed(1)}s`);
    return Response.json(data);

  } catch (error) {
    const duration = (Date.now() - startTime) / 1000;
    console.error(`[PROXY] Explanation critical failure after ${duration.toFixed(1)}s for "${topicPreview}":`, error);
    
    return Response.json(
      { status: "error", error: "Failed to connect to AI engine." },
      { status: 502 }
    );
  }
}
