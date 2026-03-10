// import { Storage } from "@google-cloud/storage";
// const bucket = new Storage().bucket(process.env.GCS_BUCKET_NAME);

// export async function uploadFile(buffer, filename, contentType) {
//   const file = bucket.file(`uploads/${filename}`);
//   await file.save(buffer, { contentType });
//   return `https://storage.googleapis.com/${process.env.GCS_BUCKET_NAME}/uploads/${filename}`;
// }

const store = {}; // in-memory, resets on server restart
export async function saveSession(id, messages) {
  store[id] = messages;
}
export async function getSession(id) {
  return { messages: store[id] || [] };
}
