"""
CarbonTrace - Mock Transparent Carbon Credit Marketplace
Run with: streamlit run carbon_credit_app.py
"""

import streamlit as st
import pandas as pd
import random
import hashlib
import json
from datetime import datetime, timedelta

st.set_page_config(page_title="CarbonTrace", page_icon="🌍", layout="wide")


# BLOCKCHAIN SIMULATION LAYER (hash-chained ledger)


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data                # dict: e.g. {"action": "ISSUE", "credit_id": "CC-1000", ...}
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        # Hashing index + timestamp + data + previous_hash means changing
        # ANY field changes this block's hash - and every block after it,
        # since each one embeds the previous block's hash.
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }


class Blockchain:
    def __init__(self):
        self.chain = [self._create_genesis_block()]

    def _create_genesis_block(self):
        return Block(0, datetime.now().isoformat(), {"action": "GENESIS", "note": "Chain start"}, "0")

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=datetime.now().isoformat(),
            data=data,
            previous_hash=previous_block.hash,
        )
        self.chain.append(new_block)
        return new_block

    def is_valid(self):
        # Walks the chain and re-derives each hash. If a block's stored
        # hash doesn't match a freshly computed one, or a block's
        # previous_hash doesn't match the prior block's actual hash,
        # someone has tampered with the ledger.
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.compute_hash():
                return False, f"Block {current.index} data does not match its stored hash (tampered)."
            if current.previous_hash != previous.hash:
                return False, f"Block {current.index} is not correctly linked to block {previous.index}."
        return True, "Chain is valid — no tampering detected."

    def as_dataframe(self):
        return pd.DataFrame([b.to_dict() for b in self.chain])


# ---------------------------------------------------------
# MOCK DATA (session_state = fake in-memory database)
# ---------------------------------------------------------

PROJECT_TYPES = ["Reforestation", "Renewable Energy", "Methane Capture", "Direct Air Capture"]
VERIFIERS = ["Verra", "Gold Standard", "Puro.earth"]

def generate_mock_credits(n=15):
    credits = []
    for i in range(n):
        ptype = random.choice(PROJECT_TYPES)
        base_price = {"Reforestation": 8, "Renewable Energy": 12,
                      "Methane Capture": 15, "Direct Air Capture": 45}[ptype]
        credits.append({
            "credit_id": f"CC-{1000+i}",
            "project_name": f"{ptype} Project #{i+1}",
            "project_type": ptype,
            "verifier": random.choice(VERIFIERS),
            "vintage_year": random.choice([2023, 2024, 2025]),
            "quality_score": round(random.uniform(5.5, 9.8), 1),
            "quantity_tonnes": random.randint(100, 5000),
            "price_per_tonne": round(base_price + random.uniform(-2, 5), 2),
            "status": "Listed",
            "seller": f"Project Developer {random.randint(1,8)}",
            "listed_date": (datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d"),
        })
    return credits

def generate_mock_trades(n=20):
    trades = []
    for i in range(n):
        trades.append({
            "trade_id": f"TX-{2000+i}",
            "credit_id": f"CC-{1000 + random.randint(0,14)}",
            "buyer": f"Company {random.choice(['A','B','C','D','E'])}",
            "quantity": random.randint(10, 500),
            "price": round(random.uniform(8, 40), 2),
            "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "retired": random.choice([True, False]),
        })
    return trades

if "credits" not in st.session_state:
    st.session_state.credits = generate_mock_credits()
if "trades" not in st.session_state:
    st.session_state.trades = generate_mock_trades()
if "next_trade_id" not in st.session_state:
    st.session_state.next_trade_id = 3000
if "ledger" not in st.session_state:
    st.session_state.ledger = Blockchain()
    # Log an ISSUE event for every mock credit so the ledger has a
    # believable starting history when the app first loads.
    for c in st.session_state.credits:
        st.session_state.ledger.add_block({
            "action": "ISSUE",
            "credit_id": c["credit_id"],
            "project_name": c["project_name"],
            "quantity_tonnes": c["quantity_tonnes"],
            "verifier": c["verifier"],
        })

# HEADER

st.title("CarbonTrace")
st.caption("A transparent, verified marketplace for carbon credits")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Dashboard", "Marketplace", "Registry", "Retire Credits", " Blockchain Ledger"]
)

# TAB 1: PUBLIC DASHBOARD

with tab1:
    st.subheader("Market Overview")

    credits_df = pd.DataFrame(st.session_state.credits)
    trades_df = pd.DataFrame(st.session_state.trades)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Credits Listed", f"{credits_df['quantity_tonnes'].sum():,} t")
    col2.metric("Total Trades", len(trades_df))
    col3.metric("Avg. Price / Tonne", f"${trades_df['price'].mean():.2f}")
    col4.metric("Total Retired", f"{trades_df[trades_df['retired']]['quantity'].sum():,} t")

    st.markdown("### Price by Project Type")
    price_by_type = credits_df.groupby("project_type")["price_per_tonne"].mean().sort_values()
    st.bar_chart(price_by_type)

    st.markdown("### Recent Trades (Public Log)")
    st.dataframe(
        trades_df.sort_values("date", ascending=False)[
            ["trade_id", "credit_id", "buyer", "quantity", "price", "date", "retired"]
        ],
        use_container_width=True,
        hide_index=True,
    )


# TAB 2: MARKETPLACE (ORDER BOOK / BUY)

with tab2:
    st.subheader("Live Marketplace")

    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        filter_type = st.multiselect("Project Type", PROJECT_TYPES, default=PROJECT_TYPES)
    with colf2:
        min_quality = st.slider("Minimum Quality Score", 0.0, 10.0, 0.0)
    with colf3:
        sort_by = st.selectbox("Sort by", ["price_per_tonne", "quality_score", "quantity_tonnes"])

    listed = credits_df[
        (credits_df["project_type"].isin(filter_type))
        & (credits_df["quality_score"] >= min_quality)
        & (credits_df["status"] == "Listed")
    ].sort_values(sort_by)

    st.markdown(f"**{len(listed)} credits available**")

    for _, row in listed.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**{row['project_name']}**  \n"
                            f"`{row['credit_id']}` · {row['project_type']} · Vintage {row['vintage_year']}")
                st.caption(f"Verified by {row['verifier']} · Quality score: {row['quality_score']}/10 · "
                          f"Seller: {row['seller']}")
            with c2:
                st.metric("Price / tonne", f"${row['price_per_tonne']}")
                st.caption(f"{row['quantity_tonnes']:,} tonnes available")
            with c3:
                qty = st.number_input("Qty", min_value=1, max_value=int(row["quantity_tonnes"]),
                                       value=1, key=f"qty_{row['credit_id']}")
                if st.button("Buy", key=f"buy_{row['credit_id']}"):
                    trade_id = f"TX-{st.session_state.next_trade_id}"
                    st.session_state.trades.append({
                        "trade_id": trade_id,
                        "credit_id": row["credit_id"],
                        "buyer": "You (Demo Buyer)",
                        "quantity": qty,
                        "price": row["price_per_tonne"],
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "retired": False,
                    })
                    st.session_state.next_trade_id += 1
                    # Log this purchase as a permanent block on the ledger
                    st.session_state.ledger.add_block({
                        "action": "BUY",
                        "trade_id": trade_id,
                        "credit_id": row["credit_id"],
                        "buyer": "You (Demo Buyer)",
                        "quantity": qty,
                        "price_per_tonne": row["price_per_tonne"],
                    })
                    st.success(f"Bought {qty} t of {row['credit_id']}. Check the Dashboard or Retire tab.")

# ---------------------------------------------------------
# TAB 3: REGISTRY (FULL VERIFIED CREDIT LIST)
# ---------------------------------------------------------
with tab3:
    st.subheader("Verified Credit Registry")
    st.caption("Every credit's full record — publicly auditable, cannot be edited once issued.")
    st.dataframe(credits_df, use_container_width=True, hide_index=True)

    st.markdown("### Look up a credit")
    lookup_id = st.selectbox("Credit ID", credits_df["credit_id"])
    record = credits_df[credits_df["credit_id"] == lookup_id].iloc[0]
    st.json(record.to_dict())


# TAB 4: RETIRE CREDITS (BURN / OFFSET
with tab4:
    st.subheader("Retire Your Credits")
    st.caption("Retiring permanently removes a credit from circulation — it can never be resold. "
              "This is the step that actually counts as an 'offset'.")

    my_trades = trades_df[(trades_df["buyer"] == "You (Demo Buyer)") & (~trades_df["retired"])]

    if my_trades.empty:
        st.info("You haven't bought any credits yet. Go to the Marketplace tab to buy some first.")
    else:
        for idx, row in my_trades.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{row['credit_id']}** · {row['quantity']} tonnes · bought {row['date']}")
                if c2.button("Retire", key=f"retire_{row['trade_id']}"):
                    for t in st.session_state.trades:
                        if t["trade_id"] == row["trade_id"]:
                            t["retired"] = True
                    # Log the retirement ("burn") as a permanent block —
                    # this is the on-chain event that makes an offset claim verifiable
                    st.session_state.ledger.add_block({
                        "action": "RETIRE",
                        "trade_id": row["trade_id"],
                        "credit_id": row["credit_id"],
                        "quantity": row["quantity"],
                        "retired_by": "You (Demo Buyer)",
                    })
                    st.success(f"{row['credit_id']} retired. This offset is now permanent and public.")
                    st.rerun()

# TAB 5: BLOCKCHAIN LEDGER (HASH-CHAIN SIMULATION)

with tab5:
    st.subheader("Blockchain Ledger")
    st.caption(
        "Every ISSUE, BUY, and RETIRE event is written here as a permanent, linked block. "
        "In production this logic would run as smart contracts on a chain like Polygon — "
        "this simulation shows the same tamper-evidence property using SHA-256 hash linking."
    )

    ledger = st.session_state.ledger
    chain_df = ledger.as_dataframe()

    col1, col2 = st.columns(2)
    col1.metric("Total Blocks", len(chain_df))
    is_valid, message = ledger.is_valid()
    col2.metric("Chain Status", "✅ Valid" if is_valid else "❌ Tampered")
    if is_valid:
        st.success(message)
    else:
        st.error(message)

    st.markdown("### Full Chain")
    st.dataframe(
        chain_df[["index", "timestamp", "data", "previous_hash", "hash"]],
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.caption("CarbonTrace — hackathon demo · all data is mock/randomly generated, resets on app restart")
