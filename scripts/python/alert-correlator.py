#!/usr/bin/env python3
"""
Alert Correlator for Multi-Source Security Alerts
Correlates alerts from multiple data sources to identify attack chains.

Usage:
    python alert-correlator.py --time-window 1800 --min-confidence medium
"""

import argparse
import json
from datetime import datetime, timedelta
from collections import defaultdict


class AlertCorrelator:
    """Correlates security alerts from multiple sources into attack chains."""
    
    ATTACK_CHAIN_PATTERNS = [
        {
            "name": "Password Spray to Compromise",
            "description": "Multiple failed logons followed by successful authentication",
            "phases": [
                {"event_codes": [4625], "min_count": 5, "time_span": 300},
                {"event_codes": [4624], "min_count": 1, "time_span": 1800}
            ],
            "severity": "HIGH",
            "mitre_techniques": ["T1110", "T1078"]
        },
        {
            "name": "Privilege Escalation After Compromise",
            "description": "Successful logon followed by privilege assignment",
            "phases": [
                {"event_codes": [4624], "min_count": 1, "time_span": 300},
                {"event_codes": [4672], "min_count": 1, "time_span": 600}
            ],
            "severity": "CRITICAL",
            "mitre_techniques": ["T1078", "T1134"]
        },
        {
            "name": "Reconnaissance to Enumeration",
            "description": "Network scanning followed by directory enumeration",
            "phases": [
                {"sources": ["opnsense"], "patterns": ["port scan", "multiple connections"], "time_span": 300},
                {"event_codes": [4625], "min_count": 1, "time_span": 1800}
            ],
            "severity": "MEDIUM",
            "mitre_techniques": ["T1046", "T1087"]
        },
        {
            "name": "Persistence Installation",
            "description": "Account or task creation after successful authentication",
            "phases": [
                {"event_codes": [4624], "min_count": 1, "time_span": 300},
                {"event_codes": [4720, 4698], "min_count": 1, "time_span": 1800}
            ],
            "severity": "CRITICAL",
            "mitre_techniques": ["T1078", "T1136.001", "T1053.005"]
        }
    ]
    
    def __init__(self, time_window=1800, min_confidence="medium"):
        self.time_window = time_window  # seconds
        self.confidence_levels = {"low": 1, "medium": 2, "high": 3}
        self.min_confidence = self.confidence_levels.get(min_confidence, 2)
        self.alerts = []
        self.correlations = []
    
    def load_alerts(self, alerts_data):
        """Load alert data from Splunk or other sources."""
        for alert in alerts_data:
            self.alerts.append({
                "timestamp": datetime.fromisoformat(alert.get("_time", datetime.now().isoformat())),
                "event_code": alert.get("EventCode", alert.get("event_code", 0)),
                "src_ip": alert.get("src_ip", "unknown"),
                "user": alert.get("Account_Name", alert.get("user", "unknown")),
                "sourcetype": alert.get("sourcetype", "unknown"),
                "raw": alert.get("_raw", "")
            })
        
        # Sort by timestamp
        self.alerts.sort(key=lambda x: x["timestamp"])
    
    def correlate(self):
        """Run correlation logic against loaded alerts."""
        for pattern in self.ATTACK_CHAIN_PATTERNS:
            matches = self._match_pattern(pattern)
            for match in matches:
                self.correlations.append({
                    "pattern_name": pattern["name"],
                    "description": pattern["description"],
                    "severity": pattern["severity"],
                    "mitre_techniques": pattern["mitre_techniques"],
                    "matched_events": match,
                    "confidence": self._calculate_confidence(match),
                    "src_ip": match[0]["src_ip"] if match else "unknown",
                    "time_range": {
                        "start": min(e["timestamp"] for e in match).isoformat(),
                        "end": max(e["timestamp"] for e in match).isoformat()
                    }
                })
        
        # Sort by severity
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        self.correlations.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        return self.correlations
    
    def _match_pattern(self, pattern):
        """Find all matches for a given attack pattern."""
        matches = []
        
        # Group alerts by source IP
        by_ip = defaultdict(list)
        for alert in self.alerts:
            by_ip[alert["src_ip"]].append(alert)
        
        for src_ip, ip_alerts in by_ip.items():
            # Try to match pattern phases in sequence
            for start_idx in range(len(ip_alerts)):
                potential_match = []
                current_idx = start_idx
                
                for phase in pattern["phases"]:
                    phase_matched = False
                    phase_events = []
                    
                    while current_idx < len(ip_alerts):
                        alert = ip_alerts[current_idx]
                        
                        # Check time span
                        if potential_match:
                            time_diff = (alert["timestamp"] - potential_match[-1]["timestamp"]).total_seconds()
                            if time_diff > phase["time_span"]:
                                break
                        
                        # Check event code match
                        if "event_codes" in phase:
                            if int(alert["event_code"]) in phase["event_codes"]:
                                phase_events.append(alert)
                        
                        # Check source type match
                        elif "sources" in phase:
                            if alert["sourcetype"] in phase["sources"]:
                                phase_events.append(alert)
                        
                        if len(phase_events) >= phase["min_count"]:
                            phase_matched = True
                            potential_match.extend(phase_events)
                            break
                        
                        current_idx += 1
                    
                    if not phase_matched:
                        break
                
                # If all phases matched, we found a chain
                if len(potential_match) >= sum(p["min_count"] for p in pattern["phases"]):
                    matches.append(potential_match)
        
        return matches
    
    def _calculate_confidence(self, matched_events):
        """Calculate confidence score for a correlation."""
        if len(matched_events) >= 10:
            return "high"
        elif len(matched_events) >= 5:
            return "medium"
        else:
            return "low"
    
    def generate_report(self):
        """Generate correlation report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "time_window_seconds": self.time_window,
            "total_alerts_analyzed": len(self.alerts),
            "correlations_found": len(self.correlations),
            "attack_chains": []
        }
        
        for corr in self.correlations:
            if self.confidence_levels.get(corr["confidence"], 0) >= self.min_confidence:
                report["attack_chains"].append({
                    "pattern": corr["pattern_name"],
                    "severity": corr["severity"],
                    "confidence": corr["confidence"],
                    "src_ip": corr["src_ip"],
                    "time_range": corr["time_range"],
                    "mitre_techniques": corr["mitre_techniques"],
                    "description": corr["description"],
                    "event_count": len(corr["matched_events"])
                })
        
        return report


def main():
    parser = argparse.ArgumentParser(description="Alert Correlator for Multi-Source Security Alerts")
    parser.add_argument("--input", "-i", help="Input JSON file with alerts")
    parser.add_argument("--output", "-o", default="correlation-report.json", help="Output file")
    parser.add_argument("--time-window", "-t", type=int, default=1800, help="Correlation time window in seconds")
    parser.add_argument("--min-confidence", choices=["low", "medium", "high"], default="medium", help="Minimum confidence level")
    
    args = parser.parse_args()
    
    correlator = AlertCorrelator(time_window=args.time_window, min_confidence=args.min_confidence)
    
    if args.input:
        with open(args.input, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            correlator.load_alerts(data)
        elif isinstance(data, dict) and "results" in data:
            correlator.load_alerts(data["results"])
        else:
            print("Error: Unrecognized JSON format")
            return
    else:
        print("No input file provided. Use --input to specify alert data.")
        print("Generating empty report template...")
    
    correlator.correlate()
    report = correlator.generate_report()
    
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Correlation report generated: {args.output}")
    print(f"Attack chains identified: {len(report['attack_chains'])}")


if __name__ == "__main__":
    main()
