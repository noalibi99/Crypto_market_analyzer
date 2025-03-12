import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import config

logger = logging.getLogger(__name__)

def send_price_alert(symbol: str, current_price: float, target_price: float, recipient_email: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg['From'] = config.SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"Price Alert - {symbol}"
        
        body = f"""
        Price Alert for {symbol}:
        Current Price: {current_price:.2f} USDT
        Target Price: {target_price:.2f} USDT
        
        This alert was generated because the price fell below your target price.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Price alert sent successfully to {recipient_email} for {symbol}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending price alert: {str(e)}")
        return False
