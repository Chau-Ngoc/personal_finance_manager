import base64
import email
import email.parser
import email.policy
import json
import os
import pprint
import re
from datetime import datetime

import boto3
import pandas as pd
from dotenv import load_dotenv

from personal_finance_manager.objects import BIDVCareDocument, BIDVHTMLDocument, BIDVSmartBankingDocument

load_dotenv()


def get_bidv_document(match: str, html_document: str) -> BIDVHTMLDocument:
    documents = {
        "bidvcare": BIDVCareDocument,
        "bidvsmartbanking": BIDVSmartBankingDocument,
    }
    return documents[match](html_document)


def get_raw_email_content(event: dict, as_bytes=False) -> str | bytes:
    sns_object = event["Records"][0]["Sns"]
    message = sns_object["Message"]
    message_dict = json.loads(message)

    content = message_dict["content"]
    if as_bytes:
        content = base64.b64decode(content)

    return content


def get_html_content(email_message: email.message.EmailMessage | email.message.Message) -> str:
    html_doc = ""
    for part in email_message.walk():
        if part.get_content_type() == "text/html":
            html_doc = part.get_content()
    return html_doc


def create_row_dict(
    document: BIDVHTMLDocument, email_message: email.message.EmailMessage | email.message.Message
) -> dict:
    csv_headers = (
        "transaction_type",
        "orig_amount",
        "orig_currency",
        "transaction_status",
        "received_time",
        "vendor",
        "approval_code",
    )

    information = document.get_meaningful_information()
    row_dict = {k: v for k, v in zip(csv_headers, information)}

    received_at = datetime.strptime(email_message["Date"], "%a, %d %b %Y %H:%M:%S %z")
    row_dict["received_time"] = received_at.isoformat()

    orig_amount, orig_currency = information[1].split(" ")
    orig_amount = float(orig_amount.replace(",", ""))
    row_dict["orig_amount"] = orig_amount
    row_dict["orig_currency"] = orig_currency

    return row_dict


def generate_keyname(prefix, at: datetime) -> str:
    this_month = at.strftime("%B-%Y")
    filename = f"{this_month}.csv"
    return f"{prefix}/{filename}"


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    email_parser = email.parser.BytesParser(policy=email.policy.SMTP)
    pattern = re.compile(r"<?(?P<specifier>\S+)@bidv\.com\.vn>?")

    # Get raw email content from SNS topic
    content_bytes = get_raw_email_content(event, as_bytes=True)

    email_message = email_parser.parsebytes(content_bytes)
    match = pattern.search(email_message["From"])

    # Parse email HTML content
    html_doc = get_html_content(email_message)
    document = get_bidv_document(match.group("specifier"), html_doc)

    row_dict = create_row_dict(document, email_message)

    # Modify the csv file in S3
    key = generate_keyname("reports", datetime.strptime(email_message["Date"], "%a, %d %b %Y %H:%M:%S %z"))
    response = s3.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)

    df = pd.read_csv(response["Body"])
    df.loc[df.shape[0]] = row_dict

    response = s3.put_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key, Body=df.to_csv(index=False).encode())
    pprint.pp(response, indent=2)

    return response
