"""
Custom Django email backend that uses Brevo (Sendinblue) API instead of SMTP.
This is needed because Railway blocks SMTP connections from deployed containers.
"""
import logging
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


class BrevoAPIBackend(BaseEmailBackend):
    """
    Email backend that sends emails using Brevo's API instead of SMTP.
    
    Required settings:
    - BREVO_API_KEY: Your Brevo API key
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        
        if not self.api_key:
            logger.warning("BREVO_API_KEY not configured. Emails will not be sent via Brevo API.")
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects using Brevo API.
        Returns the number of successfully sent messages.
        """
        if not self.api_key:
            logger.error("Cannot send email: BREVO_API_KEY not configured")
            return 0
        
        try:
            import sib_api_v3_sdk
            from sib_api_v3_sdk.rest import ApiException
        except ImportError:
            logger.error("sib-api-v3-sdk not installed. Run: pip install sib-api-v3-sdk")
            return 0
        
        # Configure API client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        num_sent = 0
        for message in email_messages:
            try:
                logger.info(f"Brevo backend received subject: '{message.subject}'")
                
                # Prepare email data for Brevo API
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    sender={"email": message.from_email},
                    to=[{"email": recipient} for recipient in message.to],
                    subject=message.subject,
                )
                
                # Handle HTML and plain text content
                if isinstance(message, EmailMultiAlternatives) and message.alternatives:
                    # Use HTML content if available
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            send_smtp_email.html_content = content
                            break
                    # Also include plain text as fallback
                    if message.body:
                        send_smtp_email.text_content = message.body
                else:
                    # Plain text only
                    send_smtp_email.text_content = message.body
                
                # Add CC and BCC if present
                if message.cc:
                    send_smtp_email.cc = [{"email": email} for email in message.cc]
                if message.bcc:
                    send_smtp_email.bcc = [{"email": email} for email in message.bcc]
                
                # Send email via Brevo API
                api_response = api_instance.send_transac_email(send_smtp_email)
                logger.info(f"Email sent successfully via Brevo API to {message.to}. Message ID: {api_response.message_id}")
                num_sent += 1
                
            except ApiException as e:
                logger.error(f"Brevo API error sending email to {message.to}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error sending email to {message.to}: {e}", exc_info=True)
                if self.fail_silently:
                    continue
                raise
        
        return num_sent
