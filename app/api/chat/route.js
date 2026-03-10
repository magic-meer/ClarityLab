import { getModel } from "@/lib/gemini";
import { saveSession, getSession } from "@/lib/firestore";
import { NextResponse } from "next/server";

export async function POST(req) {
  const { message, sessionId, level = "intermediate" } = await req.json();
  const { messages: history } = await getSession(sessionId);

  const chat = getModel().startChat({
    history,
    systemInstruction: `You are a multimodal learning assistant for a ${level} learner. 
Structure responses as: explanation → example → analogy. 
For visuals, prefix with [VISUAL]: and describe the diagram.`,
  });

  const result = await chat.sendMessage(message);
  const response = result.response.text();

  await saveSession(sessionId, [
    ...history,
    { role: "user", parts: [{ text: message }] },
    { role: "model", parts: [{ text: response }] },
  ]);

  return NextResponse.json({ response, sessionId });
}
