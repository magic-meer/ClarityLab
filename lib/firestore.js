import { Firestore } from "@google-cloud/firestore";
const db = new Firestore({ projectId: process.env.GCP_PROJECT_ID });

export async function saveSession(sessionId, messages) {
  await db.collection("sessions").doc(sessionId).set({ messages, updatedAt: new Date() });
}
export async function getSession(sessionId) {
  const doc = await db.collection("sessions").doc(sessionId).get();
  return doc.exists ? doc.data() : { messages: [] };
}
