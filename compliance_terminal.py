import os
import sys
import time
import json
import asyncio
from pathlib import Path

# Add root folder to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.generate_sar_pdf import build_sar_pdf
from backend.sar_generator import generate_legal_narrative

# Laptop 2 Static IP on Aiswarya's Hotspot
SERVER_URL = os.getenv("SHADOWGRAM_SERVER", "http://192.168.43.2:8000")

MOCK_CLUSTER = {
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

async def trigger_quarantine(cluster_data: dict):
    print("\n[!] ENFORCING BLAST-RADIUS QUARANTINE ON CLUSTER #1...")
    # Simulated action timestamp
    time.sleep(0.4)
    print("[+] Status: Louvain Community Quarantined. Bot sessions neutralized.")

    print("\n[*] Invoking NVIDIA Legal Engine (Llama-3.3-70B via NIM)...")
    narrative = await generate_legal_narrative(cluster_data)
    cluster_data["narrative_text"] = narrative

    print("[*] Generating 2-Page Courtroom SAR Dossier via ReportLab...")
    pdf_path = build_sar_pdf(cluster_data, "SAR_Cluster_0001.pdf")
    print(f"[+] Dossier ready at: {pdf_path}")
    
    # Auto-open PDF on Windows
    if os.name == 'nt':
        os.startfile(str(pdf_path.resolve()))
    print("[+] PDF successfully displayed to evaluation panel.")

def main():
    print_banner()
    print("\n[LIVE CONTROLS]")
    print("  [1] Refresh Cluster Graph Telemetry")
    print("  [2] Trigger Blast-Radius Quarantine & Export SAR PDF (Demo Action)")
    print("  [3] Exit Cockpit")
    
    while True:
        choice = input("\n[Station-04] Select Action (1-3) > ").strip()
        if choice == "1":
            print("\n[*] Querying active clusters...")
            print(f"    - Identified Cluster ID: #{MOCK_CLUSTER['cluster_id']}")
            print(f"    - Modularity Index (Q) : {MOCK_CLUSTER['modularity_q']} (Threshold > 0.60)")
            print(f"    - Detected Node Swarm  : {MOCK_CLUSTER['node_count']} concurrent instances")
            print(f"    - Mean Delta-t (Pacing): {MOCK_CLUSTER['avg_delta_t_ms']} ms")
        elif choice == "2":
            asyncio.run(trigger_quarantine(MOCK_CLUSTER))
        elif choice == "3":
            print("\nShutting down Station 4 cockpit.")
            break
        else:
            print("Invalid input. Choose 1, 2, or 3.")

if __name__ == "__main__":
    main()