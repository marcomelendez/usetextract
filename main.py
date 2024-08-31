from flask import Flask, request, jsonify
import boto3
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)




@app.route('/')
def home():
  return "Hola mundo"


@app.route('/uploadimg',methods=['POST'])

def convertImg():
    """Extracts text from an uploaded image using AWS Textract.

    Args:
        request (flask.Request): The Flask request object containing the uploaded image.

    Returns:
        list: The extracted text from the image, or an error message if unsuccessful.
    """

    if request.method != 'POST':
        return "Error: Only POST requests are supported."

    # Validate file presence and format
    if 'file_img' not in request.files:
        return jsonify({'message': 'Error: No file uploaded'}), 400
    
    file = request.files['file_img']

    if not allowed_file(file.filename):  # Implement allowed_file function
        return jsonify({'message': 'Unsupported file format.'}), 400

    # Securely store uploaded file (optional)
    # You might want to consider temporary storage or a dedicated storage service
    # to avoid saving sensitive data directly in the application directory.
    # filename = secure_filename(file.filename)
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Create a Textract client with error handling
    try:
        textract = boto3.client('textract',
                                aws_access_key_id=os.environ.get('AWS_KEY_ID'),
                                aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
                                region_name='us-east-1')
    except Exception as e:
        return jsonify({'message': 'Failed to create Textract client.'}), 400

    # Read image bytes
    try:
        image_bytes = file.read()
    except Exception as e:
        return jsonify({'message': 'Error: Failed to read image data.'}), 400
 
    # Call detect_document_text with error handling and proper response parsing
    try:
        response = textract.detect_document_text(Document={'Bytes': image_bytes})
        extracted_text = extract_text_from_response(response)  # Implement extract_text_from_response
    except Exception as e:
        return jsonify({'message': 'Failed to extract text from image.'}), 400
    
    if extracted_text:
        return extracted_text
    else:
        return jsonify({'message': 'No text found in the image.'}), 400

# Implement allowed_file function to check for supported image formats
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','jfif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Implement extract_text_from_response function to handle potential response structures
def extract_text_from_response(response):
  extractedList = []

  extracted_text = ' '

  for item in response["Blocks"]:
      if item["BlockType"] == "LINE":
        #   extracted_text += item["Text"] + '\n'  # Add newline for readability
          extractedList.append(item['Text'])
  
          
  result = {'fulltext': extracted_text.join(extractedList),'amount': extract_amount(extractedList)}
  return jsonify(result), 200

def extract_amount(collection):
    for element in collection:
        match = re.search(r'\$\s*\d+(\.\d+)?',element)
        if match:
            return match.group()



if __name__ == '__main__':
  app.run(debug=True)
    