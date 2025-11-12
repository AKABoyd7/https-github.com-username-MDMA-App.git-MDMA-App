# 🔒 Security & Deployment Guide

**CONFIDENTIAL - Internal Use Only**

Copyright © 2025 AlphaEdge AINV. All Rights Reserved.

---

## ⚠️ CRITICAL SECURITY STEPS

### 1. 🔐 Make Repository Private (DO THIS FIRST!)

```powershell
# Method 1: GitHub Web Interface
1. Go to: https://github.com/username/MDMA-App
2. Settings → Danger Zone
3. Change repository visibility → Make private
4. Confirm with repository name

# Method 2: GitHub CLI (if available)
gh repo edit --visibility private
```

**Why:** Prevent unauthorized access to proprietary code and API keys.

---

### 2. 🗑️ Remove Sensitive Keys from Public History

#### A. Remove NVIDIA API Key (if committed)

```powershell
# Check for exposed keys
git log --all --full-history --source -- .env
git log -p | findstr "NVIDIA_API_KEY"

# If keys found, use BFG Repo-Cleaner
# Download: https://rpo.jfrog.io/artifactory/bfg/
java -jar bfg.jar --replace-text passwords.txt

# Or use git-filter-repo
pip install git-filter-repo
git filter-repo --invert-paths --path .env
```

#### B. Create New Keys After Cleanup

```powershell
# Generate new NVIDIA API key
# Go to: https://build.nvidia.com/
# Regenerate API key
# Update local .env only (never commit)
```

---

### 3. 📦 Backup Strategy

#### A. Create Offline Backup

```powershell
# Full backup (code + config)
cd G:\
tar -czf AlphaEdge_AINV_backup_$(Get-Date -Format 'yyyyMMdd').tar.gz AlphaEdge_AINV\

# Or use 7-Zip with encryption
7z a -p -mhe=on AlphaEdge_AINV_backup.7z G:\AlphaEdge_AINV\
```

#### B. Backup Locations

```
PRIMARY:   G:\AlphaEdge_AINV\               (Working copy)
BACKUP 1:  G:\Backups\AlphaEdge_AINV\       (Local backup)
BACKUP 2:  External HDD                      (Offline backup)
BACKUP 3:  Encrypted cloud (Optional)        (Off-site backup)
```

#### C. What to Backup

```
✅ BACKUP:
- All source code
- Configuration files (models_config.yaml)
- Documentation
- .projectlock marker

❌ NEVER BACKUP (Regenerate on deploy):
- .env (contains keys)
- venv/ (virtual environment)
- chroma_db/ (vector database - can rebuild)
- __pycache__/ (Python cache)
- *.log (log files)
```

---

### 4. 🌿 Branch Management

#### A. Remove Public Deploy Branch (After Backup)

```powershell
# After confirming backup is complete:

# Delete remote branch (if needed)
git push origin --delete claude/alphaedge-mcp-server-011CV477Fds3K8XrtkujexEt

# Create new private production branch
git checkout -b production-internal
git push origin production-internal

# Protect production branch
# GitHub → Settings → Branches → Add rule
# Branch name: production-internal
# Enable: Require pull request reviews
```

#### B. Branch Strategy (Post-Security)

```
main                    → Public demo/docs only (no keys)
production-internal     → Private deployment branch
development-internal    → Private development branch
feature/*              → Feature branches (private)
```

---

### 5. 🔑 API Key Management

#### A. Key Storage (NEVER commit to git)

```powershell
# Create .env (local only)
@"
NVIDIA_API_KEY=nvapi-your-actual-key-here
LM_STUDIO_URL=http://localhost:1234/v1
API_HOST=0.0.0.0
API_PORT=8000
USE_NVIDIA_CLIP=false
"@ | Out-File -FilePath .env -Encoding UTF8

# Secure permissions (Windows)
icacls .env /inheritance:r
icacls .env /grant:r "${env:USERNAME}:(R,W)"
```

#### B. .gitignore Verification

```bash
# Ensure .gitignore contains:
.env
.env.*
*.key
*.pem
credentials.json
config.local.*
secrets/
```

#### C. Environment Variable Injection (Production)

```powershell
# Method 1: Windows Environment Variables
[System.Environment]::SetEnvironmentVariable("NVIDIA_API_KEY", "your-key", "Machine")

# Method 2: Secure vault (recommended)
# Use Windows Credential Manager or Azure Key Vault
```

---

### 6. 🏭 Production Deployment (Controlled Environment)

#### A. Deployment Locations (Choose One)

```
Option 1: On-Premises Server
- Hardware: Your Dual Xeon, 128GB RAM, RTX GPU
- Network: Isolated VLAN
- Access: VPN only

Option 2: Private Cloud
- Provider: Azure, AWS, GCP (Private VPC)
- Compute: GPU-enabled VM
- Access: Firewall + VPN

Option 3: Local Workstation
- Hardware: Your development machine
- Access: Localhost only (127.0.0.1)
- Firewall: Block external access
```

#### B. Production Checklist

```
Before Deployment:
[ ] Repository is PRIVATE
[ ] All API keys regenerated
[ ] .env file NOT in git
[ ] Backup completed and verified
[ ] Firewall configured
[ ] VPN access configured
[ ] SSL/TLS certificates (if web access)
[ ] Monitoring configured
[ ] Log rotation configured

After Deployment:
[ ] Test all features
[ ] Verify no key leaks
[ ] Check access logs
[ ] Verify firewall rules
[ ] Test backup restoration
```

---

### 7. 🛡️ Access Control

#### A. Network Security

```powershell
# Firewall rules (Windows)
# Block external access to API
New-NetFirewallRule -DisplayName "Block AlphaEdge API" `
  -Direction Inbound -LocalPort 8000 -Protocol TCP `
  -Action Block -RemoteAddress Internet

# Allow only localhost
New-NetFirewallRule -DisplayName "Allow AlphaEdge Local" `
  -Direction Inbound -LocalPort 8000 -Protocol TCP `
  -Action Allow -RemoteAddress 127.0.0.1
```

#### B. VPN Access (If Remote Access Needed)

```
Recommended VPN Solutions:
- WireGuard (Fast, modern)
- OpenVPN (Established, secure)
- Tailscale (Easy, zero-config)

Setup:
1. Install VPN server on deployment machine
2. Generate client certificates
3. Configure firewall to allow VPN only
4. Access platform via VPN IP
```

---

### 8. 📊 Monitoring & Auditing

#### A. Enable Logging

```python
# In .env
LOG_LEVEL=INFO
LOG_FILE=logs/platform.log
AUDIT_ENABLED=true
AUDIT_LOG=logs/audit.log
```

#### B. Monitor Access

```powershell
# Check access logs
Get-Content logs/audit.log -Tail 50

# Monitor API usage
Get-Content logs/platform.log | Select-String "POST /chat"
```

---

### 9. 🔐 Project Lock Markers (Internal Evidence)

#### A. Lock Files (Already Created)

```
.projectlock          → Machine-readable lock marker
PROJECT_STATUS.md     → Human-readable status
```

#### B. Additional Security Markers

```powershell
# Add commit signature
git config --local commit.gpgsign true

# Add security notice to README
echo "🔒 PROPRIETARY - Internal Use Only" >> README.md
```

---

### 10. 💾 Recovery Plan

#### A. Disaster Recovery Steps

```powershell
# If system compromised:

1. Immediately revoke all API keys
   → NVIDIA API: https://build.nvidia.com/
   → Regenerate immediately

2. Restore from offline backup
   → Use most recent verified backup
   → G:\Backups\AlphaEdge_AINV_backup_YYYYMMDD.tar.gz

3. Change all credentials
   → New API keys
   → New passwords
   → New certificates

4. Audit all access logs
   → Check for unauthorized access
   → Identify entry point
   → Patch vulnerability

5. Redeploy in isolated environment
   → New VPN keys
   → New firewall rules
   → Fresh installation
```

#### B. Backup Verification Schedule

```
Daily:   Automated local backup
Weekly:  Manual external backup
Monthly: Disaster recovery test
```

---

## 🎯 Quick Security Checklist

### Before ANY Deployment:

```
[ ] 1. Repository set to PRIVATE
[ ] 2. All sensitive keys removed from git history
[ ] 3. New API keys generated (not in git)
[ ] 4. .env file in .gitignore
[ ] 5. Offline backup completed
[ ] 6. Firewall rules configured
[ ] 7. Access logs enabled
[ ] 8. VPN configured (if remote access)
[ ] 9. SSL/TLS configured (if web access)
[ ] 10. Team trained on security protocols
```

---

## 📞 Emergency Contacts

```
Security Incident:
→ Revoke all keys immediately
→ Disconnect from network
→ Restore from backup
→ Investigate breach

Data Recovery:
→ Use backup from G:\Backups\
→ Follow recovery procedures
→ Verify integrity before deployment
```

---

## ⚖️ Legal Notice

```
This software and all documentation are:
- PROPRIETARY and CONFIDENTIAL
- Copyright © 2025 AlphaEdge AINV
- All Rights Reserved

Unauthorized access, use, or distribution is:
- PROHIBITED
- May result in legal action
- Subject to NDA enforcement
```

---

## 🔒 Final Security Recommendations

### 1. Immediate Actions (NOW)

```powershell
# Make repo private
# Go to GitHub → Settings → Change visibility

# Verify no keys in git history
git log -p | findstr "nvapi"

# If found, clean history and force push to private repo
```

### 2. Ongoing Security (CONTINUOUS)

```
- Weekly backup verification
- Monthly security audit
- Quarterly key rotation
- Annual disaster recovery test
```

### 3. Team Access Control

```
Access Levels:
- OWNER: Full access (you only)
- DEPLOYER: Deploy access (trusted team)
- OPERATOR: Runtime access (operators)
- VIEWER: Read-only (auditors)
```

---

## 📝 Deployment Workflow (Secure)

```
Development (Local):
   └─> Code + Test
        └─> Commit to private branch
             └─> Review + Approve
                  └─> Merge to production-internal
                       └─> Deploy to controlled environment
                            └─> Monitor + Audit
                                 └─> Backup

All steps in PRIVATE repo with VPN access only.
```

---

**🔒 Remember: Security is not a feature, it's a requirement.**

---

**Copyright © 2025 AlphaEdge AINV**
**CONFIDENTIAL - Internal Use Only**
