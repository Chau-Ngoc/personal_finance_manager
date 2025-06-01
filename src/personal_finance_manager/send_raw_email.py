import email.policy
import email.utils
import os
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from importlib.resources import read_text

import boto3


def draft_email(content: str, fromaddr: str, toaddr: str, subject: str, csv_attachment: str = None) -> EmailMessage:
    email_message = EmailMessage(policy=email.policy.SMTP)
    email_message["From"] = fromaddr
    email_message["To"] = toaddr
    email_message["Subject"] = subject
    email_message["Date"] = email.utils.formatdate(localtime=True)
    email_message.set_content(content)

    if csv_attachment:
        with open(csv_attachment, "rb") as f:
            email_message.add_attachment(
                f.read(),
                maintype="text",
                subtype="csv",
                disposition="attachment",
                filename=csv_attachment.split("/")[-1],
            )

    return email_message


def send_email(email_message: EmailMessage, host: str, port: int, username: str, password: str) -> None:
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(email_message)


def copy_example_csv_to(fp: str) -> None:
    example_csv = read_text("personal_finance_manager", "example.csv")
    with open(f"{fp}", "w") as f:
        f.write(example_csv)


def generate_month_strings(today: datetime) -> tuple[str, str]:
    this_month = today.strftime("%B-%Y")

    yesterday = today - timedelta(days=1)
    previous_month = yesterday.strftime("%B-%Y")

    return previous_month, this_month


def download_this_month_report(s3_client, bucket: str, prefix: str, fp: str, dest: str) -> None:
    key = f"{prefix}/{fp}"
    with open(f"{dest}/{fp}", "wb") as f:
        s3_client.download_fileobj(Bucket=bucket, Key=key, Fileobj=f)


def lambda_handler(event, context):
    s3 = boto3.client("s3")

    previous_month, this_month = generate_month_strings(datetime.today())

    filename = f"{previous_month}.csv"
    download_this_month_report(s3, os.environ.get("S3_BUCKET_NAME"), "reports", fp=filename, dest="/tmp")

    email_message = draft_email(
        f"Please find attached the monthly report for {previous_month}.",
        os.environ.get("EMAIL_FROM"),
        os.environ.get("EMAIL_TO"),
        f"Monthly Report - {previous_month}",
        f"/tmp/{filename}",
    )

    send_email(
        email_message,
        os.environ.get("SMTP_HOST"),
        int(os.environ.get("SMTP_PORT")),
        os.environ.get("SES_SMTP_USERNAME"),
        os.environ.get("SES_SMTP_PASSWORD"),
    )

    # Generate a report template for this month
    filename = f"{this_month}.csv"
    copy_example_csv_to(f"/tmp/{filename}")

    key = f"reports/{filename}"
    with open(f"/tmp/{filename}", "rb") as f:
        s3.put_object(Bucket=os.environ.get("S3_BUCKET_NAME"), Key=key, Body=f)
