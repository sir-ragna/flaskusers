from app import app


@app.cli.command()
def send_verification_emails():
    """sends verification emails"""
    print("print sending verification emails")