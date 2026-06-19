# Email Notification Setup and Troubleshooting

## Overview
Our platform sends email notifications for account events, system alerts, and team activity. This guide helps configure and troubleshoot email delivery issues.

---

## 1. Notification Categories

### Transactional Emails
These are essential emails that cannot be disabled:
- Password reset confirmations
- Two-factor authentication codes
- Account verification emails
- Security alerts (login from new device, password changed)

### Configurable Notifications
You can enable/disable these in Settings → Notifications → Email:
- **Billing**: Invoice generated, payment received, payment failed
- **Team**: Member joined, member left, role changed
- **System**: Scheduled maintenance, service incidents, feature updates
- **Reports**: Weekly usage summary, monthly analytics digest
- **Marketing**: Product tips, webinar invitations, feature announcements

---

## 2. Email Not Received

### Common Causes and Fixes

**Check Spam/Junk Folder**:
- Our emails come from `noreply@example.com`
- Add this address to your contacts or safe sender list

**Email Filters**:
- Check if you have inbox rules redirecting or deleting our emails
- Search your email for "example.com" to find filtered messages

**Verify Email Address**:
1. Go to Settings → Profile → Email
2. Confirm the listed email is correct and verified
3. If unverified, click "Resend Verification Email"

**Corporate Email Servers**:
- Ask your IT team to allowlist: `noreply@example.com` and `support@example.com`
- Allowlist our sending IPs: `203.0.113.10`, `203.0.113.11`
- Allowlist our SPF record: `include:_spf.example.com`

**Rate Limiting**:
- If you triggered many actions quickly, emails may be batched
- Wait 15 minutes for batch delivery
- Check notification center in-app for immediate alerts

---

## 3. Email Preferences API

For programmatic notification management:

```
PUT /v2/users/{id}/notifications
Content-Type: application/json

{
  "billing_emails": true,
  "team_emails": true,
  "system_emails": true,
  "report_emails": false,
  "marketing_emails": false
}
```

---

## 4. SMTP Integration (Enterprise)

Enterprise customers can route notifications through their own SMTP server:

1. Go to Settings → Integrations → Email
2. Select "Custom SMTP"
3. Enter your SMTP configuration:
   - Host: smtp.yourcompany.com
   - Port: 587 (TLS) or 465 (SSL)
   - Username and password
   - From address
4. Click "Test Connection"
5. Save and activate

### Troubleshooting SMTP
- Verify TLS/SSL certificate validity
- Ensure port is not blocked by firewall
- Check SMTP authentication method (PLAIN, LOGIN, CRAM-MD5)
- Review SMTP server logs for rejection reasons
