import textToSpeech from '@google-cloud/text-to-speech';

// Creates a client
const client = new textToSpeech.TextToSpeechClient();

export async function POST(request) {
  try {
    const { text, voice_name } = await request.json();

    if (!text) {
      return Response.json({ status: "error", error: "Text is required" }, { status: 400 });
    }

    const requestObj = {
      input: { text: text },
      // Select the language and SSML voice
      voice: { languageCode: 'en-US', name: voice_name || 'en-US-Journey-D' },
      // select the type of audio encoding
      audioConfig: { audioEncoding: 'MP3' },
    };

    // Performs the text-to-speech request
    const [response] = await client.synthesizeSpeech(requestObj);
    
    // Return the audio buffer as an MP3 response
    return new Response(response.audioContent, {
      status: 200,
      headers: {
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': 'inline; filename="narration.mp3"',
      },
    });
  } catch (error) {
    console.error("TTS API error:", error);
    return Response.json(
      { status: "error", error: "Failed to synthesize speech. Ensure valid Google Cloud credentials are provided." },
      { status: 500 }
    );
  }
}
