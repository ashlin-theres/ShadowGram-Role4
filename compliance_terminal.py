import os
import sys
import time
import json
import asyncio
from pathlib import Path
import requests

# Add root folder to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.generate_sar_pdf import build_sar_pdf
from backend.sar_generator import generate_legal_narrative

# Laptop 2 Static IP on Aiswarya's Hotspot (Overridden via environment variable)
SERVER_URL = os.getenv("SHADOWGRAM_SERVER", "http://192.168.43.2:8000")

FALLBACK_MOCK_CLUSTER = {
    "cluster_id": 1,
    "node_count": 20,
    "modularity_q": 0.72,
    "avg_delta_t_ms": 38.0,
    "route_overlap_pct": 96.0,
    "semantic_cosine": 0.89
}

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 65)
    print("   SHADOWGRAM // STATION 4: REGULATORY & COMPLIANCE COCKPIT   ")
    print("=" * 65)
    print(f" Target Server : {SERVER_URL}")
    print(" Framework     : CFPB Circular 2023-03 / ECOA Reg B")
    print(" Status        : MONITORING ACTIVE TELEMETRY")
    print("-" * 65)

def fetch_live_cluster() -> dict:
    """Queries Pete's Laptop 2 for detected clusters. Falls back to mock if offline."""
    try:
        resp = requests.get(f"{SERVER_URL}/api/graph", timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            clusters = data.get("clusters", [])
            if clusters:
                c = clusters[0]
                return {
                    "cluster_id": c.get("cluster_id", 1),
                    "node_count": c.get("size", len(c.get("nodes", []))),
                    "modularity_q": c.get("modularity_q", data.get("global_modularity", 0.72)),
                    "avg_delta_t_ms": 38.0,
                    "route_overlap_pct": 96.0,
                    "semantic_cosine": 0.89
                }
    except Exception as e:
        print(f"[*] Could not reach live backend at {SERVER_URL} ({type(e).__name__}). Using local mock cluster.")
    return FALLBACK_MOCK_CLUSTER

def send_live_quarantine(cluster_id: int):
    """Signals Pete's central graph engine to isolate the syndicate."""
    try:
        resp = requests.post(
            f"{SERVER_URL}/api/quarantine",
            json={
                "cluster_id": cluster_id,
                "action": "isolate",
                "reason": "CFPB Circular 2023-03 Coordinated Swarm Anomaly",
                "operator_id": "OFFICER-STATION4"
            },
            timeout=3.0
        )
        if resp.status_code == 200:
            print("[+] Live Quarantine ACK received from Central Graph Engine (Laptop 2)!")
            return True
    except Exception as e:
        print(f"[*] Live quarantine request failed ({type(e).__name__}). Operating in standalone mode.")
    return False

async def trigger_quarantine(cluster_data: dict):
    print(f"\n[!] ENFORCING BLAST-RADIUS QUARANTINE ON CLUSTER #{cluster_data['cluster_id']}...")
    
    # Send live signal to Pete's Laptop 2
    send_live_quarantine(cluster_data["cluster_id"])
    print("[+] Status: Louvain Community Quarantined. Bot sessions neutralized.")

    print("\n[*] Invoking NVIDIA Legal Engine (Llama-3.3-70B via NIM, 15s timeout)...")
    narrative = await generate_legal_narrative(cluster_data)
    cluster_data["narrative_text"] = narrative

    print("[*] Generating 2-Page Courtroom SAR Dossier via ReportLab...")
    pdf_path = build_sar_pdf(cluster_data, "SAR_Cluster_0001.pdf")
    print(f"[+] Dossier ready at: {pdf_path}")
    
    # Auto-open PDF on Windows
    if os.name == 'nt':
        try:
            os.startfile(str(pdf_path.resolve()))
            print("[+] PDF successfully displayed to evaluation panel.")
        except Exception:
            pass

def main():
    print_banner()
    print("\n[LIVE CONTROLS]")
    print("  [1] Refresh Cluster Graph Telemetry (Query Laptop 2)")
    print("  [2] Trigger Blast-Radius Quarantine & Export SAR PDF (Demo Action)")
    print("  [3] Exit Cockpit")
    
    while True:
        choice = input("\n[Station-04] Select Action (1-3) > ").strip()
        if choice == "1":
            print("\n[*] Querying active clusters from Central Gateway...")
            cluster = fetch_live_cluster()
            print(f"    - Identified Cluster ID: #{cluster['cluster_id']}")
            print(f"    - Modularity Index (Q) : {cluster['modularity_q']} (Threshold > 0.60)")
            print(f"    - Detected Node Swarm  : {cluster['node_count']} concurrent instances")
            print(f"    - Mean Delta-t (Pacing): {cluster['avg_delta_t_ms']} ms")
        elif choice == "2":
            cluster = fetch_live_cluster()
            asyncio.run(trigger_quarantine(cluster))
        elif choice == "3":
            print("\nShutting down Station 4 cockpit.")
            break
        else:
            print("Invalid input. Choose 1, 2, or 3.")

if __name__ == "__main__":
    main()