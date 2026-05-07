import re
from google import genai

# If you did Option B, this line will now work!
# If you did Option A, replace the part inside the quotes with your key.
client = genai.Client(api_key="AIzaSyCQ35hYQNoaR4v33Jj11O8_25F-EABTCNw") 

def get_medical_advice(user_input):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", # Updated for 2026
            contents=f"Analyze these symptoms: {user_input}. "
                     "Return format EXACTLY: SPECIALTY: [name], DIAGNOSIS: [conditions], PRECAUTIONS: [steps]."
        )
        
        full_text = response.text
        clean_text = full_text.replace("*", "")
        
        specialty = "General"
        diagnosis = "Analysis unavailable"
        precautions = "Please consult a doctor."

        spec_match = re.search(r"SPECIALTY:\s*(.*?)(?=,?\s*DIAGNOSIS:|$)", clean_text, re.IGNORECASE)
        diag_match = re.search(r"DIAGNOSIS:\s*(.*?)(?=,?\s*PRECAUTIONS:|$)", clean_text, re.IGNORECASE)
        prec_match = re.search(r"PRECAUTIONS:\s*(.*)", clean_text, re.IGNORECASE)

        if spec_match: specialty = spec_match.group(1).strip()
        if diag_match: diagnosis = diag_match.group(1).strip()
        if prec_match: precautions = prec_match.group(1).strip()
        
        return specialty, diagnosis, precautions

    except Exception as e:
        print(f"🚨 AI Logic Error: {e}")
        return "General Medicine", "Service currently unavailable", "Please consult a doctor immediately."