import vertexai
from google.oauth2 import service_account
from vertexai.language_models import TextGenerationModel

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    "/Users/abubkeromer/downloads/supple-student-438320-n1-c94f01cae68d.json"
)

# ✅ Pass credentials explicitly
vertexai.init(project="supple-student-438320-n1", location="us-central1", credentials=credentials)

# Load Vertex AI Model
model = TextGenerationModel.from_pretrained("text-bison@001")

# Generate AI response
response = model.predict("Analyze Bitcoin's adoption and network effects.")

print(response.text)
