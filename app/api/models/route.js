export async function GET() {
  try {
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

    const res = await fetch(`${backendUrl}/api/models`, {
      method: "GET",
      // Don't cache model list for long — refresh each time
      cache: "no-store",
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
    console.error("Models API Proxy error:", error);
    return Response.json(
      { status: "error", error: "Failed to connect to AI engine." },
      { status: 502 }
    );
  }
}
