# app.py

# --- API Key and Environment Setup ---
from dotenv import load_dotenv # Import the function needed to read the .env file
load_dotenv()                 # Execute the function to load environment variables (like API key)

# --- Import Libraries ---
from flask import Flask, render_template, request, jsonify # Import necessary Flask components for web serving
from google import genai                      # Import the Gemini SDK to interact with the model
import os

# --- Flask Application Initialization ---
app = Flask(__name__) # Initialize the Flask application instance

# --- Gemini API Setup ---
try:
    # Begin a try block to handle potential errors during client initialization
    # Uses the GEMINI_API_KEY environment variable automatically loaded by load_dotenv()
    API_KEY_VAL = os.getenv("GEMINI_API_KEY")
    
    print(API_KEY_VAL)
    client = genai.Client(api_key=API_KEY_VAL) # Create the Gemini API client object
    model_name = 'gemini-2.5-flash' # Define the specific model to be used for generation
except Exception as e:
    # If initialization fails (e.g., API key is missing)
    print(f"Error initializing Gemini Client: {e}") # Print the error to the console
    # Note: Flask will still start, but the /simplify route will fail

# --- The Wizard's Prompt ---
WIZARD_PROMPT = """
You are Bollywood, the amazing all-knowing wizard, and the guardian of the user's health. 
Translate the complex medical text provided by the user into simple, clear, 
and reassuring language that an average person can understand. 
Use a warm, empathetic tone and a reading level appropriate for all ages.
Always start with a friendly greeting like, "Greetings, fellow adventurer! 
Let's decipher this scroll together."
Use bullet points for key findings. Do not use medical jargon without immediately 
explaining it in parenthetical plain language.
""" # Define the system prompt that dictates the model's persona and rules

# --- Safety Disclaimer (Crucial!) ---
DISCLAIMER = """
<div style='font-weight: bold; color: #8B0000; padding: 10px; border: 2px solid #8B0000; margin-bottom: 15px;'>
IMPORTANT SCROLL WARNING (DISCLAIMER): 
Ignis the Hearth Dragon is an AI tool and not a medical professional. 
This explanation is for **educational purposes only** and is not a substitute for professional medical advice, diagnosis, or treatment. 
**Always consult a qualified healthcare provider** with questions about a medical condition or report.
</div>
""" # Define the essential HTML-formatted safety disclaimer

# --- Flask Route for Simplification ---
@app.route('/simplify', methods=['POST']) # Decorator defines the API endpoint and allows POST requests
def simplify_report():
    # Define the function that runs when a request hits the /simplify endpoint
    data = request.get_json() # Get the JSON payload sent from the frontend (containing the medical text)
    medical_text = data.get('text', '') # Extract the value of the 'text' key from the JSON payload

    if (not medical_text):
        # Check if the medical text field is empty
        return jsonify({'error': 'Please provide a Scroll of Findings.'}), 400 # Return an error message with HTTP status 400 (Bad Request)

        
    try:
        # Begin a try block for the API call (as it can fail due to network or key issues)
        # Build contents list for the API call
        contents = [WIZARD_PROMPT, medical_text] # Create a list containing the system prompt and the user's input
        
        # Call the Gemini API
        response = client.models.generate_content( # Send the request to the Gemini model
            model=model_name,                     # Specify the 'gemini-2.5-flash' model
            contents=contents                     # Pass the list of prompts and user text
        )
        
        # Combine disclaimer and output
        final_output = DISCLAIMER + response.text # Concatenate the safety disclaimer (HTML) and the generated text
        return jsonify({'simplified_text': final_output}) # Return the combined result as JSON to the frontend

    except Exception as e:
        # If the API call fails
        print(f"Gemini API Error: {e}") # Print the specific error to the console
        return jsonify({'error': 'The Wizard could not read the scroll (API Error).'}), 500 # Return a generic error message with HTTP status 500 (Internal Server Error)
    

# --- Flask Server Startup ---
if __name__ == '__main__':
    # This block ensures the server runs only when app.py is executed directly
    app.run(debug=True, port = 5005) # Start the Flask development server on port 5004 and enable debugging