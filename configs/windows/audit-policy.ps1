# Enable Windows Security Auditing for Active Directory Lab
# Run this script as Administrator on the Domain Controller

#Requires -RunAsAdministrator

Write-Host "=== Enabling Windows Security Auditing for SOC Lab ===" -ForegroundColor Cyan
Write-Host ""

# 1. Enable Audit Policy for Account Logon Events
Write-Host "[1/6] Enabling Account Logon auditing..." -ForegroundColor Yellow
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /set /subcategory:"Account Lockout" /success:enable /failure:enable
auditpol /set /subcategory:"IPsec Main Mode" /success:enable /failure:enable
auditpol /set /subcategory:"IPsec Quick Mode" /success:enable /failure:enable
auditpol /set /subcategory:"Other Logon/Logoff Events" /success:enable /failure:enable
auditpol /set /subcategory:"Network Policy Server" /success:enable /failure:enable
auditpol /set /subcategory:"User / Device Claims" /success:enable /failure:enable
auditpol /set /subcategory:"Group Membership" /success:enable /failure:enable

# 2. Enable Audit Policy for Account Management
Write-Host "[2/6] Enabling Account Management auditing..." -ForegroundColor Yellow
auditpol /set /subcategory:"User Account Management" /success:enable /failure:enable
auditpol /set /subcategory:"Computer Account Management" /success:enable /failure:enable
auditpol /set /subcategory:"Security Group Management" /success:enable /failure:enable
auditpol /set /subcategory:"Distribution Group Management" /success:enable /failure:enable
auditpol /set /subcategory:"Application Group Management" /success:enable /failure:enable
auditpol /set /subcategory:"Other Account Management Events" /success:enable /failure:enable

# 3. Enable Audit Policy for Logon/Logoff
Write-Host "[3/6] Enabling Logon/Logoff auditing..." -ForegroundColor Yellow
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /set /subcategory:"Logoff" /success:enable /failure:enable
auditpol /set /subcategory:"Account Lockout" /success:enable /failure:enable
auditpol /set /subcategory:"IPsec Main Mode" /success:enable /failure:enable
auditpol /set /subcategory:"IPsec Quick Mode" /success:enable /failure:enable
auditpol /set /subcategory:"Other Logon/Logoff Events" /success:enable /failure:enable
auditpol /set /subcategory:"Network Policy Server" /success:enable /failure:enable
auditpol /set /subcategory:"User / Device Claims" /success:enable /failure:enable
auditpol /set /subcategory:"Group Membership" /success:enable /failure:enable

# 4. Enable Audit Policy for Object Access
Write-Host "[4/6] Enabling Object Access auditing..." -ForegroundColor Yellow
auditpol /set /subcategory:"File System" /success:enable /failure:enable
auditpol /set /subcategory:"Registry" /success:enable /failure:enable
auditpol /set /subcategory:"Kernel Object" /success:enable /failure:enable
auditpol /set /subcategory:"SAM" /success:enable /failure:enable
auditpol /set /subcategory:"Certification Services" /success:enable /failure:enable
auditpol /set /subcategory:"Application Generated" /success:enable /failure:enable
auditpol /set /subcategory:"Handle Manipulation" /success:enable /failure:enable
auditpol /set /subcategory:"File Share" /success:enable /failure:enable
auditpol /set /subcategory:"Filtering Platform Packet Drop" /success:enable /failure:enable
auditpol /set /subcategory:"Filtering Platform Connection" /success:enable /failure:enable
auditpol /set /subcategory:"Other Object Access Events" /success:enable /failure:enable
auditpol /set /subcategory:"Detailed File Share" /success:enable /failure:enable
auditpol /set /subcategory:"Removable Storage" /success:enable /failure:enable
auditpol /set /subcategory:"Central Policy Staging" /success:enable /failure:enable

# 5. Enable Audit Policy for Policy Change
Write-Host "[5/6] Enabling Policy Change auditing..." -ForegroundColor Yellow
auditpol /set /subcategory:"Audit Policy Change" /success:enable /failure:enable
auditpol /set /subcategory:"Authentication Policy Change" /success:enable /failure:enable
auditpol /set /subcategory:"Authorization Policy Change" /success:enable /failure:enable
auditpol /set /subcategory:"MPSSVC Rule-Level Policy Change" /success:enable /failure:enable
auditpol /set /subcategory:"Filtering Platform Policy Change" /success:enable /failure:enable
auditpol /set /subcategory:"Other Policy Change Events" /success:enable /failure:enable

# 6. Enable Audit Policy for Privilege Use
Write-Host "[6/6] Enabling Privilege Use auditing..." -ForegroundColor Yellow
auditpol /set /subcategory:"Sensitive Privilege Use" /success:enable /failure:enable
auditpol /set /subcategory:"Non Sensitive Privilege Use" /success:enable /failure:enable
auditpol /set /subcategory:"Other Privilege Use Events" /success:enable /failure:enable

Write-Host ""
Write-Host "=== Audit Policy Configuration Complete ===" -ForegroundColor Green
Write-Host ""

# Verify settings
Write-Host "Current audit policy settings:" -ForegroundColor Cyan
auditpol /get /category:*

Write-Host ""
Write-Host "Note: For these changes to take full effect, you may need to restart the computer." -ForegroundColor Yellow
Write-Host "Also ensure the Splunk Universal Forwarder is configured to monitor Security logs." -ForegroundColor Yellow
