# Account Management Guide

## Overview
This guide covers all aspects of managing your user account, including profile updates, team management, and security settings.

---

## 1. Profile Settings

### Updating Personal Information
1. Log into your account at `https://app.example.com`
2. Click your avatar in the top-right corner
3. Select "Profile Settings"
4. Update any of the following fields:
   - Display Name
   - Email Address (requires re-verification)
   - Phone Number
   - Timezone
   - Language Preference
5. Click "Save Changes"

### Profile Photo
- Supported formats: JPG, PNG, GIF
- Maximum file size: 5 MB
- Recommended dimensions: 200x200 pixels
- Photos are cropped to a circle in the UI

---

## 2. Team Management

### Inviting Team Members
1. Go to Settings → Team → Members
2. Click "Invite Member"
3. Enter the email address
4. Select a role:
   - **Viewer**: Read-only access to dashboards and reports
   - **Editor**: Can create and modify resources
   - **Admin**: Full access including billing and user management
   - **Owner**: Complete control, can transfer ownership
5. Click "Send Invitation"
6. The invited user receives an email with a signup/login link

### Removing Team Members
1. Go to Settings → Team → Members
2. Find the user in the list
3. Click the three-dot menu → "Remove Member"
4. Confirm the removal
5. The user immediately loses access to all shared resources

### Transferring Ownership
- Only the current Owner can transfer ownership
- Navigate to Settings → Team → Transfer Ownership
- Select the new owner from the team list
- Confirm with your password and 2FA code
- The transfer is immediate and irreversible

---

## 3. Notification Preferences

### Email Notifications
Configure which emails you receive:
- **Account Alerts**: Password changes, login from new device (cannot be disabled)
- **Product Updates**: New features, maintenance windows
- **Billing Alerts**: Invoice generated, payment processed, payment failed
- **Team Activity**: Member joined, member removed, role changed
- **Marketing**: Tips, best practices, webinar invitations

### In-App Notifications
- Real-time alerts appear in the notification bell icon
- Click to view details, mark as read, or dismiss
- Configure notification sound: Settings → Notifications → Sound

### Webhook Notifications
- For programmatic integration, set up webhook notifications
- See the API Troubleshooting Guide for webhook configuration details

---

## 4. Data Export

### Exporting Your Data
You can export all your account data at any time:
1. Go to Settings → Account → Data Export
2. Select the data types to include:
   - Profile information
   - Usage history
   - Support ticket history
   - Billing records
3. Choose format: JSON or CSV
4. Click "Generate Export"
5. You'll receive a download link via email within 24 hours

### Data Retention
- Active accounts: Data retained indefinitely
- Cancelled accounts: Data retained for 90 days
- Deleted accounts: All data permanently removed within 30 days
- Compliance: We follow GDPR, CCPA, and SOC 2 standards
