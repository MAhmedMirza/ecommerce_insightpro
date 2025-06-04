from flask import Flask, render_template_string, request, jsonify
from werkzeug.utils import secure_filename
import os

# Create the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# HTML Template for the upload page with enhanced UI/UX
upload_html = ('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce InsightPro</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
            --accent-color: #4cc9f0;
            --light-color: #f8f9fa;
            --dark-color: #212529;
            --success-color: #4bb543;
            --error-color: #ff3333;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f5f7fa;
            color: var(--dark-color);
            line-height: 1.6;
        }

        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px 0;
            box-shadow: var(--shadow);
            position: relative;
            z-index: 100;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 600;
            background: linear-gradient(to right, #fff, #e0e0e0);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            animation: fadeIn 1s ease;
        }

        .user-info {
            display: flex;
            align-items: center;
            position: relative;
            cursor: pointer;
        }

        #userAvatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
            object-fit: cover;
            border: 2px solid white;
            transition: var(--transition);
        }

        .username {
            font-weight: 500;
            display: flex;
            align-items: center;
            transition: var(--transition);
        }

        .username:hover {
            color: var(--accent-color);
        }

        .dropdown-arrow {
            margin-left: 5px;
            transition: var(--transition);
        }

        .dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            background: white;
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: 10px 0;
            width: 150px;
            display: none;
            opacity: 0;
            transform: translateY(-10px);
            transition: var(--transition);
            z-index: 10;
        }

        .dropdown.show {
            display: block;
            opacity: 1;
            transform: translateY(0);
            animation: fadeInDropdown 0.3s ease;
        }

        .dropdown button {
            display: block;
            width: 100%;
            padding: 8px 15px;
            text-align: left;
            background: none;
            border: none;
            color: var(--dark-color);
            cursor: pointer;
            transition: var(--transition);
        }

        .dropdown button:hover {
            background: #f0f0f0;
            color: var(--primary-color);
        }

        main {
            padding: 40px 0;
            min-height: calc(100vh - 150px);
        }

        .upload-section {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: var(--shadow);
            text-align: center;
            max-width: 800px;
            margin: 0 auto;
            transform: translateY(20px);
            opacity: 0;
            animation: fadeInUp 0.8s ease forwards;
        }

        .upload-section h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: var(--primary-color);
        }

        .instructions {
            margin-bottom: 30px;
            color: #555;
        }

        .upload-container {
            position: relative;
            margin: 30px auto;
            width: 100%;
            max-width: 400px;
        }

        .upload-button {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 30px;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }

        .upload-button:hover {
            border-color: var(--primary-color);
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }

        .upload-button.drag-over {
            border-color: var(--success-color);
            background-color: rgba(75, 181, 67, 0.05);
        }

        #fileInput {
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            opacity: 0;
            cursor: pointer;
        }

        .upload-icon {
            font-size: 2.5rem;
            color: var(--primary-color);
            margin-bottom: 15px;
            transition: var(--transition);
        }

        .upload-text {
            font-weight: 500;
            color: var(--primary-color);
            margin-bottom: 10px;
            transition: var(--transition);
        }

        .supported-formats {
            font-size: 0.9rem;
            color: #777;
            margin-top: 10px;
        }

        .error-message {
            color: var(--error-color);
            margin-top: 15px;
            font-size: 0.9rem;
            display: none;
            animation: shake 0.5s ease;
        }

        .success-message {
            color: var(--success-color);
            margin-top: 15px;
            font-size: 0.9rem;
            display: none;
        }

        .progress-container {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-top: 20px;
            overflow: hidden;
            display: none;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        footer {
            background: var(--dark-color);
            color: white;
            text-align: center;
            padding: 20px 0;
            font-size: 0.9rem;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInDropdown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                text-align: center;
            }

            .user-info {
                margin-top: 15px;
            }

            .upload-section {
                padding: 30px 20px;
            }

            h1 {
                font-size: 1.5rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="header-content">
                <h1>E-Commerce InsightPro</h1>
                <div class="user-info" id="userInfo">
                    <img src="https://ui-avatars.com/api/?name=Muhammad+Ahmed+Mirza&background=random" alt="User Avatar" id="userAvatar">
                    <p class="username" onclick="toggleDropdown(event)">
                        Muhammad Ahmed Mirza
                        <span class="dropdown-arrow" id="dropdownArrow">&#9660;</span>
                    </p>
                    <div class="dropdown" id="userDropdown">
                        <button><i class="fas fa-user"></i> Profile</button>
                        <button><i class="fas fa-sign-out-alt"></i> Logout</button>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main>
        <section class="upload-section" id="uploadSection">
            <div class="container">
                <h2>Upload file to get better Insights</h2>
                <p class="instructions">Please ensure that your dataset includes the following columns for accurate processing:<br>
                    <strong>Product Name, Category, Order Date, Quantity, and Total Amount.</strong><br>
                    Missing any of these columns will result in upload errors.</p>
                
                <div class="upload-container">
                    <div class="upload-button" id="uploadButton">
                        <input type="file" id="fileInput" name="file" accept=".csv" required>
                        <div class="upload-icon">
                            <i class="fas fa-cloud-upload-alt"></i>
                        </div>
                        <div class="upload-text">SELECT OR DRAG DATASET</div>
                        <div class="supported-formats">Supported format: CSV files only</div>
                    </div>
                    <p class="error-message" id="errorMessage">Unsupported file format. Please upload a CSV file.</p>
                    <p class="success-message" id="successMessage">File uploaded successfully! Processing data...</p>
                    <div class="progress-container" id="progressContainer">
                        <div class="progress-bar" id="progressBar"></div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2024 E-Commerce InsightPro. All rights reserved.</p>
        </div>
    </footer>

    <script>
        // DOM Elements
        const userInfo = document.getElementById('userInfo');
        const dropdown = document.getElementById('userDropdown');
        const dropdownArrow = document.getElementById('dropdownArrow');
        const uploadButton = document.getElementById('uploadButton');
        const fileInput = document.getElementById('fileInput');
        const errorMessage = document.getElementById('errorMessage');
        const successMessage = document.getElementById('successMessage');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const uploadSection = document.getElementById('uploadSection');

        // Toggle dropdown menu
        function toggleDropdown(event) {
            event.stopPropagation();
            dropdown.classList.toggle('show');
            dropdownArrow.innerHTML = dropdown.classList.contains('show') ? '&#9650;' : '&#9660;';
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!userInfo.contains(event.target)) {
                dropdown.classList.remove('show');
                dropdownArrow.innerHTML = '&#9660;';
            }
        });

        // Drag and drop functionality
        uploadButton.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadButton.classList.add('drag-over');
        });

        uploadButton.addEventListener('dragleave', () => {
            uploadButton.classList.remove('drag-over');
        });

        uploadButton.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadButton.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileUpload();
            }
        });

        // File input change handler
        fileInput.addEventListener('change', handleFileUpload);

        function handleFileUpload() {
            const file = fileInput.files[0];
            
            // Reset messages
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';
            
            // Validate file
            if (!file) return;
            
            if (!file.name.endsWith('.csv')) {
                errorMessage.style.display = 'block';
                return;
            }
            
            // Show upload in progress
            uploadButton.style.pointerEvents = 'none';
            progressContainer.style.display = 'block';
            
            // Simulate progress (in a real app, this would be actual upload progress)
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 10;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(progressInterval);
                    
                    // Complete upload
                    setTimeout(() => {
                        uploadFile(file);
                    }, 300);
                }
                progressBar.style.width = `${progress}%`;
            }, 200);
        }

        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    errorMessage.textContent = data.error;
                    errorMessage.style.display = 'block';
                } else {
                    successMessage.style.display = 'block';
                    // Add a checkmark animation
                    const uploadIcon = document.querySelector('.upload-icon i');
                    uploadIcon.classList.remove('fa-cloud-upload-alt');
                    uploadIcon.classList.add('fa-check-circle');
                    uploadIcon.style.color = 'var(--success-color)';
                    
                    // Redirect or perform next steps after a delay
                    setTimeout(() => {
                        // Here you would typically redirect to the analysis page
                        console.log('File uploaded successfully:', data.filename);
                    }, 1500);
                }
            })
            .catch(error => {
                errorMessage.textContent = 'Upload failed. Please try again.';
                errorMessage.style.display = 'block';
                console.error('Error uploading file:', error);
            })
            .finally(() => {
                progressContainer.style.display = 'none';
                progressBar.style.width = '0%';
                uploadButton.style.pointerEvents = 'auto';
            });
        }

        // Add some interactive animations
        uploadButton.addEventListener('mouseenter', () => {
            const icon = document.querySelector('.upload-icon i');
            icon.style.animation = 'pulse 1.5s infinite';
        });

        uploadButton.addEventListener('mouseleave', () => {
            const icon = document.querySelector('.upload-icon i');
            icon.style.animation = '';
        });
    </script>
</body>
</html>
''')

# Route to display the upload page
@app.route('/')
def home():
    return render_template_string(upload_html)

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        }), 200
    else:
        return jsonify({'error': 'Invalid file format. Only CSV allowed.'}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)