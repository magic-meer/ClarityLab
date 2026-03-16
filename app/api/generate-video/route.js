import http from "http";

export const maxDuration = 300; // 5 minutes (standard for Vercel/Cloud Run long tasks)

export async function POST(request) {
  const startTime = Date.now();
  let topicPreview = "Unknown";
  
  try {
    const body = await request.json();
    topicPreview = body.prompt ? body.prompt.slice(0, 50) : "No Prompt";
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8080";
    const url = new URL(`${backendUrl}/api/generate-video`);

    console.log(`[PROXY] Starting video generation for: "${topicPreview}"`);

    // Use http.request to bypass undici's default HeadersTimeoutError
    const resPromise = new Promise((resolve, reject) => {
      const req = http.request({
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        timeout: 600000, // 10 minute timeout
      }, (res) => {
        let data = "";
        res.on("data", (chunk) => { data += chunk; });
        res.on("end", () => {
          resolve({
            ok: res.statusCode >= 200 && res.statusCode < 300,
            status: res.statusCode,
            data: data
          });
        });
      });

      req.on("error", (e) => reject(e));
      req.on("timeout", () => {
        req.destroy();
        reject(new Error("Backend request timed out (10 min limit)"));
      });
      req.write(JSON.stringify(body));
      req.end();
    });

    const result = await resPromise;
    const duration = (Date.now() - startTime) / 1000;

    if (!result.ok) {
      console.error(`[PROXY] Video Backend Error (${result.status}) after ${duration.toFixed(1)}s:`, result.data);
      let errorMsg = "Backend error";
      try {
        const parsed = JSON.parse(result.data);
        errorMsg = parsed.detail || parsed.error || errorMsg;
      } catch (e) {}
      
      return Response.json(
        { status: "error", error: errorMsg },
        { status: result.status }
      );
    }

    console.log(`[PROXY] Video Generation SUCCESS for "${topicPreview}" in ${duration.toFixed(1)}s`);
    return Response.json(JSON.parse(result.data));

  } catch (error) {
    const duration = (Date.now() - startTime) / 1000;
    console.error(`[PROXY] Video API critical failure after ${duration.toFixed(1)}s for "${topicPreview}":`, error);
    
    return Response.json(
      { status: "error", error: `Failed to generate video: ${error.message}` },
      { status: 502 }
    );
  }
}
