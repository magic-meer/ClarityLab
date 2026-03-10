import { getModel } from "@/lib/gemini";
import { uploadFile } from "@/lib/storage";
import { NextResponse } from "next/server";

export async function POST(req) {
  const formData = await req.formData();
  const file = formData.get("file");
  const question = formData.get("question") || "Explain this learning material.";
  const buffer = Buffer.from(await file.arrayBuffer());

  const url = await uploadFile(buffer, `${Date.now()}-${file.name}`, file.type);
  const result = await getModel().generateContent([
    question,
    { inlineData: { data: buffer.toString("base64"), mimeType: file.type } },
  ]);

  return NextResponse.json({ response: result.response.text(), fileUrl: url });
}
