import textToSpeech from "@google-cloud/text-to-speech";
import { NextResponse } from "next/server";

const client = new textToSpeech.TextToSpeechClient();

export async function POST(req) {
  const { text } = await req.json();
  const [result] = await client.synthesizeSpeech({
    input: { text },
    voice: { languageCode: "en-US", ssmlGender: "NEUTRAL" },
    audioConfig: { audioEncoding: "MP3" },
  });
  return new NextResponse(result.audioContent, {
    headers: { "Content-Type": "audio/mpeg" },
  });
}
