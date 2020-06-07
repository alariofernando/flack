# Project 2

Web Programming with Python and JavaScript

### How to use it

1. Install python 3.7+
2. python -m venv venv
3. Activate the virtual environment (./venv/Scripts/activate || ./venv/bin/activate)
4. Install libraries (pip install -r requirements.txt)
5. Set the SECRET e FLASK_APP variables
6. Set the UPLOAD_FOLDER and S3_BUCKET
7. Set the bucket name in the terraform/main.tf folder
8. Navigate to main.tf folder and run "terraform init && terraform apply -auto-approve" (You must have an AWS account!)
9. flask run !!