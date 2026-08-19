#!/usr/bin/env python3
"""
Log Parser and Analyzer for Windows Security Events
Parses exported Windows Event Logs and generates attack timeline reports.

Usage:
    python log-parser.py --file security.evtx --output report.json
    python log-parser.py --splunk-query "index=main sourcetype=WinEventLog"
"""

import argparse
import json
import csv
import sys
from datetime import datetime
from collections import defaultdict, Counter


class WindowsEventParser:
    """Parser for Windows Security Event Log entries."""
    
    EVENT_CODES = {
        4624: "Successful Logon",
        4625: "Failed Logon",
        4634: "Logoff",
        4648: "Explicit Credential Logon",
        4672: "Special Privileges Assigned",
        4698: "Scheduled Task Created",
        4720: "User Account Created",
        4722: "User Account Enabled",
        4732: "Member Added to Group",
        4740: "Account Locked Out",
        4768: "Kerberos Authentication Ticket Requested",
        4769: "Kerberos Service Ticket Requested",
        4771: "Kerberos Pre-Auth Failed",
        4776: "NTLM Authentication",
        5140: "Network Share Accessed",
        5145: "Network Share Object Checked"
    }
    
    def __init__(self):
        self.events = []
        self.timeline = defaultdict(list)
        self.src_ip_stats = Counter()
        self.user_stats = Counter()
        self.event_code_stats = Counter()
    
    def parse_json_events(self, events_json):
        """Parse events from JSON format (Splunk export)."""
        for event in events_json:
            parsed = self._parse_single_event(event)
            if parsed:
                self.events.append(parsed)
                self._update_stats(parsed)
    
    def _parse_single_event(self, event):
        """Extract relevant fields from a single event."""
        try:
            event_code = int(event.get("EventCode", 0))
            timestamp = event.get("_time", event.get("TimeCreated", ""))
            
            parsed = {
                "timestamp": timestamp,
                "event_code": event_code,
                "event_desc": self.EVENT_CODES.get(event_code, "Unknown"),
                "computer": event.get("ComputerName", "Unknown"),
                "user": event.get("Account_Name", event.get("user", "Unknown")),
                "src_ip": event.get("src_ip", event.get("Source_Network_Address", "Unknown")),
                "src_port": event.get("src_port", event.get("Source_Port", "Unknown")),
                "logon_type": event.get("Logon_Type", "N/A"),
                "process": event.get("ProcessName", "N/A"),
                "raw": event.get("_raw", "")
            }
            return parsed
        except Exception as e:
            print(f"Warning: Failed to parse event: {e}", file=sys.stderr)
            return None
    
    def _update_stats(self, event):
        """Update internal statistics counters."""
        hour_key = event["timestamp"][:13] if len(event["timestamp"]) >= 13 else event["timestamp"]
        self.timeline[hour_key].append(event)
        
        if event["src_ip"] != "Unknown":
            self.src_ip_stats[event["src_ip"]] += 1
        
        if event["user"] != "Unknown":
            self.user_stats[event["user"]] += 1
        
        self.event_code_stats[event["event_code"]] += 1
    
    def detect_brute_force(self, threshold=5):
        """Detect potential brute force attacks."""
        brute_force_ips = []
        
        for ip, count in self.src_ip_stats.items():
            if count >= threshold and ip != "Unknown":
                # Check if this IP has both 4625 and 4624 events
                failed = sum(1 for e in self.events if e["src_ip"] == ip and e["event_code"] == 4625)
                success = sum(1 for e in self.events if e["src_ip"] == ip and e["event_code"] == 4624)
                
                brute_force_ips.append({
                    "src_ip": ip,
                    "total_events": count,
                    "failed_attempts": failed,
                    "successful_logons": success,
                    "risk_score": "HIGH" if success > 0 else "MEDIUM"
                })
        
        return sorted(brute_force_ips, key=lambda x: x["total_events"], reverse=True)
    
    def generate_timeline(self):
        """Generate attack timeline grouped by hour."""
        timeline_report = []
        
        for hour in sorted(self.timeline.keys()):
            events = self.timeline[hour]
            event_codes = Counter(e["event_code"] for e in events)
            
            timeline_report.append({
                "hour": hour,
                "total_events": len(events),
                "event_breakdown": dict(event_codes),
                "unique_sources": len(set(e["src_ip"] for e in events if e["src_ip"] != "Unknown")),
                "unique_users": len(set(e["user"] for e in events if e["user"] != "Unknown"))
            })
        
        return timeline_report
    
    def generate_summary(self):
        """Generate overall summary statistics."""
        return {
            "total_events": len(self.events),
            "time_range": {
                "start": min(e["timestamp"] for e in self.events) if self.events else None,
                "end": max(e["timestamp"] for e in self.events) if self.events else None
            },
            "event_breakdown": dict(self.event_code_stats),
            "top_source_ips": dict(self.src_ip_stats.most_common(10)),
            "top_users": dict(self.user_stats.most_common(10)),
            "brute_force_candidates": self.detect_brute_force()
        }
    
    def export_json(self, filepath):
        """Export full analysis to JSON."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.generate_summary(),
            "timeline": self.generate_timeline(),
            "events": self.events
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report exported to {filepath}")
    
    def export_csv(self, filepath):
        """Export events to CSV."""
        if not self.events:
            print("No events to export")
            return
        
        fieldnames = ["timestamp", "event_code", "event_desc", "computer", 
                      "user", "src_ip", "src_port", "logon_type", "process"]
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for event in self.events:
                writer.writerow({k: event.get(k, "") for k in fieldnames})
        
        print(f"CSV exported to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Windows Security Event Log Parser")
    parser.add_argument("--file", "-f", help="Input JSON file (Splunk export)")
    parser.add_argument("--output", "-o", default="report.json", help="Output file path")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("--brute-threshold", type=int, default=5, help="Brute force detection threshold")
    
    args = parser.parse_args()
    
    if not args.file:
        print("Error: Please provide an input file with --file")
        sys.exit(1)
    
    # Load events
    try:
        with open(args.file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)
    
    # Handle both single array and Splunk result format
    if isinstance(data, list):
        events = data
    elif isinstance(data, dict) and "results" in data:
        events = data["results"]
    else:
        print("Error: Unrecognized JSON format. Expected array or {results: [...]}")
        sys.exit(1)
    
    # Parse and analyze
    parser = WindowsEventParser()
    parser.parse_json_events(events)
    
    # Print summary
    summary = parser.generate_summary()
    print("\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)
    print(f"Total Events: {summary['total_events']}")
    print(f"Time Range: {summary['time_range']['start']} to {summary['time_range']['end']}")
    print(f"\nEvent Breakdown:")
    for code, count in summary['event_breakdown'].items():
        desc = parser.EVENT_CODES.get(int(code), "Unknown")
        print(f"  Event {code} ({desc}): {count}")
    
    print(f"\nBrute Force Candidates (threshold={args.brute_threshold}):")
    for ip_data in summary['brute_force_candidates']:
        print(f"  {ip_data['src_ip']}: {ip_data['failed_attempts']} failed, "
              f"{ip_data['successful_logons']} success [{ip_data['risk_score']}]")
    
    # Export
    if args.format == "json":
        parser.export_json(args.output)
    else:
        parser.export_csv(args.output)


if __name__ == "__main__":
    main()
