"""
PDF Generator Helper Script.

One-time script to generate the required password_reset_guide.pdf document
for the knowledge base. Uses fpdf2 to create a realistic PDF with proper
formatting, sections, and step-by-step instructions.

Usage:
    python generate_pdf.py
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos


class PasswordResetPDF(FPDF):
    """Custom PDF class for the Password Reset Guide."""

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Password Reset & Account Recovery Guide", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 6, "Document Version 2.0 | Last Updated: January 2024", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(5)
        # Draw a line
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} | Confidential - Internal Support Document", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(240, 240, 250)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(3)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def step_item(self, step_num, text):
        self.set_font("Helvetica", "B", 10)
        self.cell(8, 5, f"{step_num}.")
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def bullet_item(self, text):
        self.set_font("Helvetica", "", 10)
        self.cell(5, 5, "-")
        self.multi_cell(0, 5, f" {text}")
        self.ln(1)


def generate_password_reset_pdf():
    """Generate the password_reset_guide.pdf file."""
    pdf = PasswordResetPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Page 1: Overview and Standard Reset ──
    pdf.add_page()

    pdf.section_title("1. Overview")
    pdf.body_text(
        "This guide provides step-by-step instructions for resetting your password, "
        "recovering your account, and managing two-factor authentication (2FA). "
        "These procedures apply to all account types including Free, Pro, and Enterprise plans."
    )
    pdf.body_text(
        "If you are unable to complete the password reset process using the methods below, "
        "please contact our support team at support@example.com or call +1-800-555-HELP (4357)."
    )

    pdf.section_title("2. Standard Password Reset (Email Verification)")
    pdf.body_text("Follow these steps to reset your password via email verification:")

    pdf.step_item(1, "Navigate to the login page at https://app.example.com/login")
    pdf.step_item(2, 'Click the "Forgot Password?" link below the password field')
    pdf.step_item(3, "Enter the email address associated with your account")
    pdf.step_item(4, 'Click "Send Reset Link" - you will receive an email within 2-5 minutes')
    pdf.step_item(5, "Check your inbox (and spam/junk folder) for the reset email from noreply@example.com")
    pdf.step_item(6, 'Click the "Reset Password" button in the email (link expires in 24 hours)')
    pdf.step_item(7, "Enter your new password meeting the following requirements:")
    pdf.bullet_item("Minimum 12 characters")
    pdf.bullet_item("At least one uppercase letter (A-Z)")
    pdf.bullet_item("At least one lowercase letter (a-z)")
    pdf.bullet_item("At least one number (0-9)")
    pdf.bullet_item("At least one special character (!@#$%^&*)")
    pdf.bullet_item("Cannot match your previous 5 passwords")
    pdf.step_item(8, "Confirm the new password by entering it again")
    pdf.step_item(9, 'Click "Update Password" to complete the reset')
    pdf.step_item(10, "You will be redirected to the login page. Sign in with your new password.")

    pdf.body_text(
        "Important: The password reset link is single-use and expires after 24 hours. "
        "If the link has expired, you will need to request a new one by repeating the steps above."
    )

    # ── Page 2: 2FA Recovery ──
    pdf.section_title("3. Two-Factor Authentication (2FA) Recovery")
    pdf.body_text(
        "If you have lost access to your authenticator app or device, follow these "
        "recovery procedures based on your available backup options."
    )

    pdf.sub_title("Option A: Using Backup Recovery Codes")
    pdf.body_text(
        "When you initially set up 2FA, you were provided with 10 one-time backup "
        "recovery codes. Each code can only be used once."
    )
    pdf.step_item(1, "On the 2FA verification screen, click 'Use a recovery code instead'")
    pdf.step_item(2, "Enter one of your unused backup recovery codes")
    pdf.step_item(3, "After logging in, go to Settings > Security > Two-Factor Authentication")
    pdf.step_item(4, "Disable and re-enable 2FA with your new authenticator device")
    pdf.step_item(5, "Save the new set of backup codes in a secure location")

    pdf.sub_title("Option B: SMS Backup Verification")
    pdf.body_text(
        "If you configured SMS as a backup 2FA method during setup:"
    )
    pdf.step_item(1, "On the 2FA verification screen, click 'Try another method'")
    pdf.step_item(2, "Select 'Text message' option")
    pdf.step_item(3, "A 6-digit code will be sent to your registered phone number")
    pdf.step_item(4, "Enter the code within 10 minutes (codes expire after 10 minutes)")
    pdf.step_item(5, "Once logged in, update your primary 2FA method")

    pdf.sub_title("Option C: Identity Verification (Last Resort)")
    pdf.body_text(
        "If you have lost access to both your authenticator and backup codes, "
        "you must verify your identity manually:"
    )
    pdf.step_item(1, "Send an email to security@example.com with subject '2FA Recovery Request'")
    pdf.step_item(2, "Include your registered email address and account username")
    pdf.step_item(3, "Attach a photo of a valid government-issued ID (passport, driver's license)")
    pdf.step_item(4, "Our security team will verify your identity within 24-48 hours")
    pdf.step_item(5, "Once verified, 2FA will be temporarily disabled on your account")
    pdf.step_item(6, "Log in and set up 2FA again immediately")

    # ── Page 3: Account Lockout and Admin Reset ──
    pdf.add_page()

    pdf.section_title("4. Account Lockout Procedures")
    pdf.body_text(
        "For security purposes, accounts are automatically locked after 5 consecutive "
        "failed login attempts. The lockout duration depends on the number of lockouts:"
    )
    pdf.bullet_item("First lockout: 15 minutes")
    pdf.bullet_item("Second lockout: 30 minutes")
    pdf.bullet_item("Third lockout: 1 hour")
    pdf.bullet_item("Fourth lockout and beyond: 24 hours (contact support to unlock)")

    pdf.body_text("To unlock your account:")
    pdf.step_item(1, "Wait for the lockout period to expire, then try again with the correct password")
    pdf.step_item(2, "Alternatively, use the 'Forgot Password' flow to reset your password, "
                     "which also unlocks the account")
    pdf.step_item(3, "If you are locked out for 24 hours or more, contact support with your "
                     "account email for manual unlock")

    pdf.section_title("5. Admin-Initiated Password Reset")
    pdf.body_text(
        "Organization administrators can force a password reset for team members:"
    )
    pdf.step_item(1, "Log into the admin console at https://admin.example.com")
    pdf.step_item(2, "Navigate to Users > Team Members")
    pdf.step_item(3, "Search for the user by name or email")
    pdf.step_item(4, "Click the user's profile > Security > 'Force Password Reset'")
    pdf.step_item(5, "The user will receive an email with a mandatory password reset link")
    pdf.step_item(6, "The user must reset their password within 72 hours or the link expires")
    pdf.body_text(
        "Note: Admin-initiated resets are logged in the audit trail. The affected user "
        "receives a notification that their password was reset by an administrator."
    )

    pdf.section_title("6. Password Security Best Practices")
    pdf.bullet_item("Use a unique password for each service - never reuse passwords")
    pdf.bullet_item("Use a password manager (e.g., 1Password, LastPass, Bitwarden) to generate and store strong passwords")
    pdf.bullet_item("Enable 2FA on all accounts that support it")
    pdf.bullet_item("Never share your password via email, chat, or phone")
    pdf.bullet_item("Be cautious of phishing emails asking you to reset your password")
    pdf.bullet_item("Change your password immediately if you suspect it has been compromised")
    pdf.bullet_item("Review your active sessions regularly: Settings > Security > Active Sessions")

    pdf.section_title("7. Frequently Asked Questions")

    pdf.sub_title("Q: How often should I change my password?")
    pdf.body_text("A: Passwords expire every 90 days. You will receive a reminder 14 days before expiration.")

    pdf.sub_title("Q: Can I use the same password again?")
    pdf.body_text("A: No. The system remembers your last 5 passwords and prevents reuse.")

    pdf.sub_title("Q: What if I never received the reset email?")
    pdf.body_text(
        "A: Check your spam/junk folder first. If not there, verify the email address on file is correct. "
        "Corporate email servers may block our emails - ask your IT team to allowlist noreply@example.com. "
        "You can also try requesting the reset again after 5 minutes."
    )

    pdf.sub_title("Q: Is there a way to reset without email access?")
    pdf.body_text(
        "A: If you no longer have access to your registered email, contact support at "
        "support@example.com from any email with your account details and government ID "
        "for identity verification."
    )

    # Save the PDF
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "password_reset_guide.pdf")
    pdf.output(output_path)
    print(f"[OK] Generated: {output_path}")


if __name__ == "__main__":
    generate_password_reset_pdf()
