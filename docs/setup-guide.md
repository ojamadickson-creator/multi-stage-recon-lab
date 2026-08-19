# Detailed Lab Setup Guide

## Prerequisites

Before you begin, ensure you have the following:

* **Virtualization Platform:** Oracle VirtualBox 7.0+ or VMware Workstation 17+
* **Host Machine Specifications:**
  * CPU: 4 cores minimum (8 recommended)
  * RAM: 16GB minimum (24GB+ recommended)
  * Storage: 100GB free space
  * OS: Windows 10/11, macOS, or Linux host
* **ISO Images:**
  * Windows Server 2016/2019 Evaluation
  * Windows 10 Pro ISO
  * Kali Linux ISO
  * OPNsense ISO
  * Ubuntu Server 20.04/22.04 LTS

## Step by Step Setup

### Step 1: Create Virtual Networks

#### In VirtualBox

1. Open VirtualBox Manager
2. Navigate to **File > Tools > Network Manager**
3. Create NAT Network:
   * Name: `NatNetwork`
   * IPv4 Prefix: `192.168.57.0/24`
   * Enable DHCP: Yes
4. Create Host Only Network:
   * Name: `vboxnet0`
   * IPv4 Address: `192.168.56.1`
   * IPv4 Network Mask: `255.255.255.0`
   * Disable DHCP (we'll use static IPs)

### Step 2: Deploy OPNsense Firewall

1. Create new VM:
   * Name: `OPNsense Firewall`
   * Type: BSD
   * Version: FreeBSD 64 bit
   * RAM: 1GB
   * Disk: 8GB

2. Add network adapters:
   * Adapter 1: NAT Network (`NatNetwork`)
   * Adapter 2: Host Only (`vboxnet0`)

3. Install OPNsense:
   * Boot from ISO
   * Follow installation wizard
   * Select default options

4. Configure interfaces:
   * WAN (em0): Accept DHCP or set static `192.168.57.254/24`
   * LAN (em1): Set static `192.168.56.254/24`

5. Complete web setup:
   * Access `https://192.168.56.254` from host
   * Complete initial wizard
   * Set admin password

### Step 3: Deploy Domain Controller

1. Create new VM:
   * Name: `WIN2016 DC`
   * Type: Microsoft Windows
   * Version: Windows 2016 (64 bit)
   * RAM: 4GB
   * Disk: 60GB

2. Configure network:
   * Adapter 1: Host Only (`vboxnet0`)

3. Install Windows Server:
   * Select Windows Server 2016/2019 Standard (Desktop Experience)
   * Set administrator password

4. Configure static IP:
   ```powershell
   New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.56.102 -PrefixLength 24 -DefaultGateway 192.168.56.254
   Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses 127.0.0.1
   ```

5. Install Active Directory Domain Services:
   ```powershell
   Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
   Import-Module ADDSDeployment
   Install-ADDSForest -DomainName "windomain.local" -InstallDns
   ```

6. Create lab user:
   ```powershell
   New-ADUser -Name "vagrant" -SamAccountName vagrant -UserPrincipalName vagrant@windomain.local -AccountPassword (ConvertTo-SecureString "vagrant" -AsPlainText -Force) -Enabled $true
   Add-ADGroupMember -Identity "Domain Users" -Members vagrant
   ```

### Step 4: Deploy Windows 10 Workstation

1. Create new VM:
   * Name: `WIN10 Mgmt`
   * Type: Microsoft Windows
   * Version: Windows 10 (64 bit)
   * RAM: 4GB
   * Disk: 60GB

2. Configure network:
   * Adapter 1: Host Only (`vboxnet0`)

3. Install Windows 10 Pro

4. Configure static IP:
   ```powershell
   New-NetIPAddress -InterfaceAlias "Ethernet" -IPAddress 192.168.56.104 -PrefixLength 24 -DefaultGateway 192.168.56.254
   Set-DnsClientServerAddress -InterfaceAlias "Ethernet" -ServerAddresses 192.168.56.102
   ```

5. Join domain:
   ```powershell
   Add-Computer -DomainName windomain.local -Credential windomain\administrator -Restart
   ```

### Step 5: Deploy Splunk Server

1. Create new VM:
   * Name: `Splunk SIEM`
   * Type: Linux
   * Version: Ubuntu 64 bit
   * RAM: 4GB
   * Disk: 80GB

2. Configure network:
   * Adapter 1: Host Only (`vboxnet0`)

3. Install Ubuntu Server:
   * Select minimal installation
   * Set hostname: `splunk`
   * Create user: `splunkadmin`

4. Configure static IP:
   ```bash
   sudo nano /etc/netplan/00-installer-config.yaml
   ```
   ```yaml
   network:
     version: 2
     ethernets:
       enp0s3:
         dhcp4: no
         addresses:
           - 192.168.56.106/24
         routes:
           - to: default
             via: 192.168.56.254
         nameservers:
           addresses: [192.168.56.102]
   ```
   ```bash
   sudo netplan apply
   ```

5. Install Splunk Enterprise:
   ```bash
   cd /tmp
   wget https://download.splunk.com/products/splunk/releases/9.1.2/linux/splunk-9.1.2-b6b9c8185839-Linux-x86_64.tgz
   sudo tar -xzf splunk-*.tgz -C /opt
   sudo /opt/splunk/bin/splunk start --accept-license
   sudo /opt/splunk/bin/splunk enable boot-start
   ```

6. Configure inputs for Windows events and syslog:
   ```bash
   sudo mkdir -p /opt/splunk/etc/apps/soc_lab/local
   ```
   Create `inputs.conf` as documented in `configs/splunk/inputs.conf`

### Step 6: Deploy Kali Linux

1. Create new VM:
   * Name: `Kali Attacker`
   * Type: Linux
   * Version: Debian 64 bit
   * RAM: 4GB
   * Disk: 60GB

2. Configure network:
   * Adapter 1: NAT Network (`NatNetwork`)

3. Install Kali Linux:
   * Use Kali Linux installer ISO
   * Select default options
   * Create user: `kali`

4. Configure static IP:
   ```bash
   sudo nano /etc/network/interfaces
   ```
   ```
   auto eth0
   iface eth0 inet static
       address 192.168.57.10
       netmask 255.255.255.0
       gateway 192.168.57.254
   ```

5. Install required tools:
   ```bash
   sudo apt update
   sudo apt install -y nmap ldap-utils netexec
   ```

### Step 7: Install Splunk Universal Forwarder on DC

1. On Windows Server, download Splunk Universal Forwarder
2. Run installer as Administrator
3. During installation:
   * Set receiving indexer: `192.168.56.106:9997`
4. After installation, configure inputs:
   ```powershell
   cd "C:\Program Files\SplunkUniversalForwarder\bin"
   .\splunk.exe add monitor "Security" -index main -sourcetype WinEventLog
   .\splunk.exe restart
   ```

### Step 8: Configure OPNsense Syslog Forwarding

1. Log in to OPNsense web interface
2. Go to **System > Settings > Logging / Targets**
3. Add remote target:
   * Transport: UDP (Legacy)
   * Hostname: `192.168.56.106`
   * Port: `514`
   * Categories: Firewall

### Step 9: Configure Firewall Rules

1. In OPNsense, go to **Firewall > Rules > Floating**
2. Add rules to allow Kali traffic:
   * Protocol: Any
   * Source: `192.168.57.10`
   * Destination: `192.168.56.102`
   * Action: Pass
   * Description: `Kali_Allow`
   * Enable logging: Yes

### Step 10: Verify Everything Works

Run the health check script:
```bash
./scripts/bash/health-check.sh
```

Or manually verify:
1. From Kali: `ping 192.168.56.102`
2. From Kali: `nmap -Pn 192.168.56.102`
3. From Win10: Open browser to `http://192.168.56.106:8000`
4. In Splunk: Search `index=main | stats count by sourcetype`

## Post Installation Checklist

* [ ] All VMs boot successfully
* [ ] Network connectivity verified between all systems
* [ ] Splunk Web UI accessible from Win10
* [ ] Windows events appearing in Splunk
* [ ] Firewall logs appearing in Splunk
* [ ] Kali can reach DC through firewall
* [ ] All static IPs correctly configured
* [ ] DNS resolution working
* [ ] Domain join successful on Win10
* [ ] Syslog forwarding configured on OPNsense

## Troubleshooting Common Issues

### Kali has no internet
* Check NAT Network configuration in VirtualBox
* Verify OPNsense WAN interface has correct IP
* Check OPNsense outbound NAT rules

### Windows 10 cannot join domain
* Verify DNS points to DC (192.168.56.102)
* Check DC is running DNS service
* Verify network connectivity: `ping windomain.local`

### Splunk not receiving events
* Check Universal Forwarder status on DC
* Verify Splunk is listening on 9997: `netstat -tulpn | grep 9997`
* Test connectivity from DC: `Test-NetConnection 192.168.56.106 -Port 9997`
* Check Splunk internal logs for errors

### No firewall logs in Splunk
* Verify OPNsense syslog target configuration
* Check Splunk UDP input on port 514
* Test with: `echo "test" | nc -u 192.168.56.106 514`
* Check for firewall blocking syslog

## Next Steps

Once your lab is operational:

1. Run the reconnaissance script: `./configs/kali/recon.sh`
2. Execute the password spray: `./configs/kali/password-spray.sh`
3. Import SPL queries from `spl-queries/` into Splunk
4. Build dashboards using the queries
5. Configure alerts for detection
6. Document your findings

Happy hunting!
