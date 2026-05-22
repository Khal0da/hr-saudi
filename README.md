# HR Saudi - Enterprise Workforce Platform

Enterprise HR management platform built on ERPNext/Frappe Framework for construction and hotel operations in Saudi Arabia.

## Overview

A complete workforce operating system managing the full employee lifecycle from recruitment to exit, with multi-company support, biometric integration, and mobile attendance.

## Features

### Biometric & Attendance
- **ZKTeco Integration** via Biometric Bridge Service
- **GPS Attendance** for sites without devices
- **QR Code** check-in verification
- **Geo-Fencing** to prevent off-site attendance
- **Offline Mode** with auto-sync
- Auto **Late & OT Calculation**

### Workforce Management
- **Crew Management** - Team-based workforce
- **Workforce Allocation Engine** - Smart worker distribution
- **Mobilization / Demobilization** - Site transfers
- **Labor Camp Management** - Housing & bed allocation

### Recruitment
- Manpower & Visa Requests
- Candidate Evaluation
- Recruitment SLA Tracking
- Visa Quota Management

### Payroll
- **Branch-based Payroll** - Payroll per location
- Project-based cost allocation
- Dynamic OT Engine
- **WPS Integration** (Wage Protection System)
- Auto **GOSI Calculation**
- Multi-company support

### Compliance
- **Saudization (Nitaqat)** tracking
- **Saudi Labor Law** engine
- Document expiry alerts (Iqama, Passport, License)
- HSE integration

### Mobile Attendance (PWA)
- GPS check-in/out from any location
- QR Code scanning
- Works offline
- Full Arabic RTL interface

### Integration
- Seamless integration with `construction_app`
- Project-based employee tracking
- Subcontractor workforce management
- Cost center allocation

## Installation

```bash
bench get-app https://github.com/Khal0da/hr-saudi.git
bench install-app hr_saudi
```

## Biometric Bridge Setup

```bash
cd apps/hr_saudi/hr_saudi/bridge/
pip install -r requirements.txt
cp config_template.yaml config.yaml
# Edit config.yaml with your ERPNext credentials and device IPs
python bridge.py
```

### Windows Service Installation

```batch
cd apps\hr_saudi\hr_saudi\bridge\
install_service.bat
```

## Mobile Attendance

Open in browser:
```
https://your-erpnext.com/attendance/?employee=EMP-001
```

## License

MIT
