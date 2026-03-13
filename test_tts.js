const textToSpeech = require('@google-cloud/text-to-speech');
const fs = require('fs');
const util = require('util');

// Initialize the client
const client = new textToSpeech.TextToSpeechClient();

async function testTTS() {
  const text = 'Hello, this is a test of the text to speech API.';
  
  const request = {
    input: { text: text },
    voice: { languageCode: 'en-US', name: 'en-US-Journey-D' },
    audioConfig: { audioEncoding: 'MP3' },
  };

  try {
    console.log("Sending request to Google Cloud TTS...");
    const [response] = await client.synthesizeSpeech(request);
    
    const writeFile = util.promisify(fs.writeFile);
    await writeFile('test_audio_output.mp3', response.audioContent, 'binary');
    
    console.log('Success! Audio content written to file "test_audio_output.mp3"');
  } catch (error) {
    console.error('Error during TTS test:', error);
  }
}

testTTS();
