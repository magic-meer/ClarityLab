import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

print(f"Using Project: {PROJECT_ID}, Location: {LOCATION}")

if not PROJECT_ID or not LOCATION:
    print("Error: Please make sure GCP_PROJECT_ID and GCP_LOCATION are set in your .env file.")
    exit(1)

# Initialize the Vertex AI client
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

print("Sending request to Vertex AI Imagen 3...")
try:
    # Generate an image with a simple prompt
    result = client.models.generate_images(
        model='imagen-3.0-generate-001',
        prompt='A simple red apple on a white background, low detail',
        config=genai.types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/jpeg",
            aspect_ratio="1:1"
        )
    )

    if not result.generated_images:
        print("No images were generated.")
        exit(1)

    generated_image = result.generated_images[0]
    
    # Save the generated image
    image_path = "test_image_output.jpg"
    with open(image_path, "wb") as f:
        f.write(generated_image.image.image_bytes)
        
    print(f"Success! Image saved to: {os.path.abspath(image_path)}")
    
except Exception as e:
    print(f"An error occurred: {e}")
