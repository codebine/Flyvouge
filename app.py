from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import smtplib
from email.message import EmailMessage

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# File storage setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Excel files for storing form submissions
JOB_APPLICATIONS_FILE = "job_applications.xlsx"
ENQUIRY_FILE = "enquiries.xlsx"

# Email Configuration
SENDER_EMAIL = "varshith.sunbright@gmail.com"
SENDER_PASSWORD = "umqdsmvhcnlcxckj"  # Use an App Password instead of your Gmail password
RECIPIENT_EMAIL = "saivarshith.nomuluri@gmail.com"

# ----------------------- Contact Form Submission -----------------------
@app.route("/submit-contact-form", methods=["POST"])
def submit_contact_form():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        if not name or not email or not subject or not message:
            return jsonify({"success": False, "message": "All fields are required."}), 400

        # Send email notification
        email_subject = f"New Contact Form Submission: {subject}"
        email_body = f"""
        You have received a new message:

        Name: {name}
        Email: {email}
        Subject: {subject}
        Message: {message}
        """

        send_email(email_subject, email_body)

        return jsonify({"success": True, "message": "✅ Your message has been sent successfully!"})

    except Exception as e:
        print("Error in contact form submission:", e)
        return jsonify({"success": False, "message": "❌ Error submitting contact form"}), 500


# ----------------------- Job Application Submission -----------------------
@app.route("/submit-job-application", methods=["POST"])
def submit_job_application():
    try:
        full_name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        position = request.form.get("position")
        resume = request.files.get("resume")

        if not full_name or not email or not phone or not position or not resume:
            return jsonify({"success": False, "message": "All fields must be filled, including resume."}), 400

        # Save resume file
        resume_filename = os.path.join(UPLOAD_FOLDER, resume.filename)
        resume.save(resume_filename)

        # Save application to Excel
        data = {"Name": full_name, "Email": email, "Phone": phone, "Position": position, "Resume": resume_filename}
        df = pd.DataFrame([data])

        if os.path.exists(JOB_APPLICATIONS_FILE):
            df.to_csv(JOB_APPLICATIONS_FILE, mode="a", header=False, index=False)
        else:
            df.to_csv(JOB_APPLICATIONS_FILE, mode="w", header=True, index=False)

        # Send email with resume attachment
        subject = f"New Job Application for {position}"
        body = f"""
        New Job Application received:
        Name: {full_name}
        Email: {email}
        Phone: {phone}
        Position: {position}

        Resume is attached with this email.
        """
        send_email_with_attachment(subject, body, resume_filename)

        return jsonify({"success": True, "message": "✅ Your job application has been submitted successfully!"})

    except Exception as e:
        print("Error in job application:", e)
        return jsonify({"success": False, "message": "❌ Error processing job application"}), 500


# ----------------------- Course Enquiry Submission -----------------------
@app.route("/submit-application-enquiry", methods=["POST"])
def submit_application_enquiry():
    try:
        application_type = request.form.get("application_type")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        course = request.form.get("course")
        message = request.form.get("message", "")

        if not application_type or not full_name or not email or not phone or not course:
            return jsonify({"success": False, "message": "All required fields must be filled."}), 400

        # Save to Excel
        data = {
            "Type": application_type,
            "Name": full_name,
            "Email": email,
            "Phone": phone,
            "Course": course,
            "Message": message
        }
        df = pd.DataFrame([data])

        if os.path.exists(ENQUIRY_FILE):
            df.to_csv(ENQUIRY_FILE, mode="a", header=False, index=False)
        else:
            df.to_csv(ENQUIRY_FILE, mode="w", header=True, index=False)

        # Send email notification
        subject = f"New {application_type.capitalize()} for {course}"
        body = f"""
        New {application_type.capitalize()} received:
        Name: {full_name}
        Email: {email}
        Phone: {phone}
        Course: {course}
        Message: {message}
        """

        send_email(subject, body)

        return jsonify({"success": True, "message": "✅ Your course enquiry has been submitted successfully!"})

    except Exception as e:
        print("Error in application enquiry:", e)
        return jsonify({"success": False, "message": "❌ Error processing course enquiry"}), 500


# ----------------------- Email Functions -----------------------
def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Error sending email:", e)


def send_email_with_attachment(subject, body, file_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content(body)

        # Attach resume file
        with open(file_path, "rb") as attachment:
            file_data = attachment.read()
            file_name = os.path.basename(file_path)
            msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print("✅ Email with attachment sent successfully!")
    except Exception as e:
        print("❌ Error sending email with attachment:", e)


# ----------------------- Start Flask Server -----------------------
if __name__ == "__main__":
    app.run(debug=True)
