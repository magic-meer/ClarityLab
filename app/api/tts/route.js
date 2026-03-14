import textToSpeech from '@google-cloud/text-to-speech';

/**
 * Lazily create a single TextToSpeech client.
 * This:
 * - Avoids recreating the client per request
 * - Allows Cloud Run / local dev to inject credentials via env vars
 */
let ttsClient = null;
function getTtsClient() {
  if (!ttsClient) {
    const clientConfig = {};

    // Optional: allow passing service-account JSON via env var
    // TEXT_TO_SPEECH_CREDENTIALS should contain the full JSON string.
    if (process.env.TEXT_TO_SPEECH_CREDENTIALS) {
      try {
        clientConfig.credentials = JSON.parse(process.env.TEXT_TO_SPEECH_CREDENTIALS);
      } catch (err) {
        console.warn("Failed to parse TEXT_TO_SPEECH_CREDENTIALS JSON:", err);
      }
    }

    ttsClient = new textToSpeech.TextToSpeechClient(clientConfig);
  }
  return ttsClient;
}

export async function POST(request) {
  try {
    const { text, voice_name } = await request.json();

    if (!text || typeof text !== "string" || !text.trim()) {
      return Response.json(
        { status: "error", error: "Text is required for narration." },
        { status: 400 }
      );
    }

    const voiceName = voice_name || "en-US-Journey-D";

    const requestObj = {
      input: { text: text.trim() },
      voice: {
        languageCode: "en-US",
        name: voiceName,
      },
      audioConfig: {
        audioEncoding: "MP3",
      },
    };

    const client = getTtsClient();

    // Performs the text-to-speech request
    const [response] = await client.synthesizeSpeech(requestObj);

    if (!response || !response.audioContent) {
      return Response.json(
        { status: "error", error: "Text-to-Speech API returned an empty response." },
        { status: 502 }
      );
    }

    // Return the audio buffer as an MP3 response
    return new Response(response.audioContent, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Disposition": 'inline; filename="narration.mp3"',
      },
    });
  } catch (error) {
    console.error("TTS API error:", error);

    const message =
      error?.message?.includes("could not load the default credentials") ||
      error?.message?.includes("No valid") ||
      error?.code === 16
        ? "Failed to synthesize speech. Google Cloud credentials are missing or invalid."
        : "Failed to synthesize speech. Please try again.";

    return Response.json(
      {
        status: "error",
        error: message,
        details: process.env.NODE_ENV === "development" ? String(error) : undefined,
      },
      { status: 500 }
    );
  }
}
