class Email:
    def __init__(self, user_email: str, subject: str, body: str, summary: str = None):
        self.user_email = user_email
        self.subject = subject
        self.body = body
        self.summary = summary

    def to_dict(self):
        return {
            "user_email": self.user_email,
            "subject": self.subject,
            "body": self.body,
            "summary": self.summary
        }
