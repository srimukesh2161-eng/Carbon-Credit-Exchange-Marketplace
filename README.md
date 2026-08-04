# CarbonTrace

A transparent, verified marketplace for carbon credits — built as a personal learning project exploring full-stack development, blockchain principles, and real-world carbon market regulation.

## Overview

CarbonTrace simulates a carbon credit marketplace addressing a real problem in today's carbon markets: fragmented registries, double-counting risk, and lack of public accountability make it difficult to verify whether a credit is genuine or has already been used to offset emissions.

The platform combines a live trading marketplace, a public verified registry, a permanent retirement system, and a custom blockchain-style ledger to demonstrate how transparency and tamper-evidence can be built into a carbon credit system from the ground up.

## Features

- **Live Marketplace** — Browse and purchase carbon credits filtered by project type, quality score, and price, across categories including reforestation, renewable energy, methane capture, and direct air capture.
- **Public Registry** — View the full, auditable record of every credit issued, including project origin, verifier, vintage year, and current status.
- **Retirement System** — Permanently retire ("burn") a purchased credit to offset emissions. Retired credits can never be resold or reused.
- **Public Dashboard** — Real-time market statistics, price trends by project type, and a transparent trade history log.
- **Blockchain Ledger** — Every issuance, purchase, and retirement event is recorded as a permanent, hash-linked block. Tampering with any past record breaks the chain and is instantly detectable.

## How the Blockchain Layer Works

Each block stores its data along with a SHA-256 hash of the previous block, creating a tamper-evident chain:

- `Block.compute_hash()` — hashes the block's index, timestamp, data, and previous hash together
- `Blockchain.add_block()` — links each new block to the last block's hash
- `Blockchain.is_valid()` — walks the full chain, recomputing hashes to verify nothing has been altered

This simulates the core tamper-evidence property of a real blockchain without requiring wallets, gas fees, or a live network — in production, this logic would be deployed as smart contracts on a low-cost chain such as Polygon.

## Real-World Grounding

The platform's registry design (unique credit IDs, vintage years, double-counting prevention) was informed by research into India's Carbon Credit Trading Scheme (CCTS), a real regulatory framework administered by the Bureau of Energy Efficiency (BEE) that sets mandatory greenhouse gas emissions intensity targets for energy-intensive industries.

## Tech Stack

- **Frontend/App:** Python, Streamlit
- **Data Handling:** Pandas
- **Blockchain Simulation:** Python (`hashlib`, `json`) — custom `Block` and `Blockchain` classes using SHA-256 hashing

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone <your-repo-url>
cd carbon-credit-exchange-platform
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install streamlit pandas
```

### Running the App

```bash
streamlit run carbon_credit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

## Project Structure

```
carbon-credit-exchange-platform/
├── carbon_credit_app.py   # Main Streamlit application
├── README.md               # This file
└── venv/                   # Virtual environment (not tracked in git)
```

## Roadmap / Future Work

- [ ] Integrate real project data from Verra's public registry API
- [ ] Connect IoT-based gas sensors (ESP32 + MQ-series sensors) for independent emissions verification
- [ ] Deploy the blockchain simulation as an actual smart contract on Polygon testnet
- [ ] Add a verifier approval workflow to simulate independent third-party verification
- [ ] Persistent database (replacing in-memory session state) for multi-session data

## Disclaimer

This is a personal learning and portfolio project. All market data, companies, and transactions are simulated/mock data. This platform does not facilitate real financial transactions and is not affiliated with or endorsed by any official carbon credit registry or regulatory body.

## License

This project is for personal/educational use.

## Author

Built by Asgalimba (kreisel) as part of an ongoing exploration into full-stack development, blockchain concepts, and climate tech.
