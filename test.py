from google import genai
import inspect
print(inspect.getsourcefile(genai.Client))
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
api=
client = genai.Client(api_key=api)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents=""
)
print(response.text)