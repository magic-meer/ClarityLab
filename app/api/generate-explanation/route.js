export async function POST(request) {
  try {
    const body = await request.json();
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8080";

    const res = await fetch(`${backendUrl}/api/generate-explanation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
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
    console.error("Explanation API proxy error:", error);
    return Response.json(
      { status: "error", error: "Failed to connect to AI engine." },
      { status: 502 }
    );
  }
}
