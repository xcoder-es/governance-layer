"""
app.py — Streamlit dashboard for the Governance Layer.

Usage:
    streamlit run src/governance/dashboard/app.py
    streamlit run src/governance/dashboard/app.py -- --neo4j

Connects to Neo4j Aura if .env has valid credentials.
Loads experiment results from results/ directory.
"""

import os
import sys
import argparse

import streamlit as st

from ..ontology.memory_backend import MemoryBackend
from ..prove.predictions import ALL_PREDICTIONS

st.set_page_config(
    page_title="Governance Layer — Formal Framework",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--neo4j", action="store_true", help="Connect to Neo4j Aura")
    args, _ = parser.parse_known_args()
    return args


@st.cache_resource
def get_ontology_backend(use_neo4j: bool = False):
    if use_neo4j:
        try:
            from ..ontology.neo4j_backend import Neo4jBackend
            backend = Neo4jBackend()
            backend.get_identity_vector()
            return backend
        except Exception as e:
            st.sidebar.warning(f"Neo4j connection failed: {e}. Falling back to memory.")
            return MemoryBackend()
    return MemoryBackend()


def main():
    args = _parse_args()
    backend = get_ontology_backend(use_neo4j=args.neo4j)

    st.sidebar.title("🏛️ Governance Layer")
    st.sidebar.caption("Formal Framework for Self-Governing AI")

    backend_type = "Neo4j Aura" if args.neo4j and "Neo4jBackend" in str(type(backend)) else "Memory (local)"
    st.sidebar.info(f"**Ontology**: {backend_type}")

    if not backend.get_identity_vector():
        backend.set_identity_vector([1.0, 1.0, 1.0, 0.95, 0.9])

    tab_names = ["📐 Formal Model", "🏛️ Parliament Live", "📊 Benchmarks"]
    tab_model, tab_parliament, tab_benchmarks = st.tabs(tab_names)

    with tab_model:
        from .model_tab import render_model_tab
        render_model_tab(backend)

    with tab_parliament:
        from .parliament_tab import render_parliament_tab
        render_parliament_tab()

    with tab_benchmarks:
        from .benchmarks_tab import render_benchmarks_tab
        render_benchmarks_tab()


if __name__ == "__main__":
    main()
