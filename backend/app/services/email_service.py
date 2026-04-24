import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _cfg() -> dict:
    """Read SMTP settings fresh on every call so .env changes apply without restart."""
    user = os.getenv("SMTP_USER", "")
    return {
        "host":         os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port":         int(os.getenv("SMTP_PORT", "465")),
        "user":         user,
        "password":     os.getenv("SMTP_PASSWORD", ""),
        "from":         os.getenv("SMTP_FROM", "") or user,
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "timeout":      int(os.getenv("SMTP_TIMEOUT", "15")),
    }


def _build_message(from_addr: str, to_email: str, display_name: str, verify_url: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your Novera account"
    msg["From"] = f"Novera <{from_addr}>"
    msg["To"] = to_email

    text_body = f"""\
Hi {display_name},

Thanks for signing up for Novera — the carbon-aware shopping platform.

Please verify your email address by visiting:
{verify_url}

This link expires in 24 hours. If you didn't create an account, you can ignore this email.

— The Novera Team
"""

    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
             background:#f9fafb;margin:0;padding:40px 0;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;
                    border:1px solid #e5e7eb;overflow:hidden;">
        <tr>
          <td style="background:#16a34a;padding:28px 40px;">
            <span style="color:#fff;font-size:22px;font-weight:700;
                         letter-spacing:-0.5px;">🌿 Novera</span>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px;">
            <h1 style="margin:0 0 8px;font-size:22px;color:#111827;">
              Verify your email address
            </h1>
            <p style="margin:0 0 24px;color:#6b7280;font-size:15px;line-height:1.6;">
              Hi <strong>{display_name}</strong>, thanks for joining Novera!
              Click the button below to verify your email and start shopping sustainably.
            </p>
            <a href="{verify_url}"
               style="display:inline-block;background:#16a34a;color:#fff;
                      text-decoration:none;font-weight:600;font-size:15px;
                      padding:13px 28px;border-radius:8px;">
              Verify Email Address
            </a>
            <p style="margin:28px 0 0;color:#9ca3af;font-size:13px;line-height:1.5;">
              This link expires in <strong>24 hours</strong>.<br>
              If you didn't create an account, you can safely ignore this email.
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 40px;border-top:1px solid #f3f4f6;">
            <p style="margin:0;color:#d1d5db;font-size:12px;">
              Can't click the button? Copy and paste this link:<br>
              <a href="{verify_url}" style="color:#16a34a;">{verify_url}</a>
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def send_verification_email(to_email: str, display_name: str, token: str) -> None:
    cfg = _cfg()

    if not cfg["user"] or not cfg["password"]:
        raise RuntimeError("SMTP_USER and SMTP_PASSWORD must be set in .env")

    verify_url = f"{cfg['frontend_url']}/verify-email?token={token}"
    msg = _build_message(cfg["from"], to_email, display_name, verify_url)
    raw = msg.as_string()

    # Port 465 → SMTP_SSL (implicit TLS)
    # Port 587 → STARTTLS
    if cfg["port"] == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=cfg["timeout"], context=context) as smtp:
            smtp.login(cfg["user"], cfg["password"])
            smtp.sendmail(cfg["from"], to_email, raw)
    else:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=cfg["timeout"]) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(cfg["user"], cfg["password"])
            smtp.sendmail(cfg["from"], to_email, raw)
