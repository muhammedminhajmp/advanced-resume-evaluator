# from flask import Flask, request, jsonify
# import os
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# # Set the upload folder and allowed extensions
# app.config['UPLOAD_FOLDER'] = './uploads'
# app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# # Function to check allowed file extensions
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# # Endpoint to handle file upload
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     print("Request files:", request.files)  # Debugging log
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
    
#     file = request.files['file']
#     print("Uploaded file:", file)  # Debugging log
    
#     if file.filename == '':
#         return jsonify({'error': 'No file selected'}), 400
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
#         return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
#     else:
#         return jsonify({'error': 'File type not allowed'}), 400

# if __name__ == '__main__':
#     # Ensure the uploads folder exists
#     if not os.path.exists('./uploads'):
#         os.makedirs('./uploads')
#     app.run(debug=True)


import secrets

print(secrets.token_hex(24))  # Example: '6f7f8e3d45e7483f7d5c2e2b467b3a11'





