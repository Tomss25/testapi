import streamlit as st
import requests

BASE_URL = "https://api.polygon.io"

# Mappatura strategica degli endpoint
ENDPOINTS = {
    "Stocks - Last Trade": {"url": "/v2/last/trade/{ticker}", "inputs": ["ticker"]},
    "Stocks - Daily Open / Close": {"url": "/v1/open-close/{ticker}/{date}", "inputs": ["ticker", "date"]},
    "Forex - Previous Close": {"url": "/v2/aggs/ticker/C:{ticker}/prev", "inputs": ["ticker"]},
    "Crypto - Daily Open / Close": {"url": "/v1/open-close/crypto/{crypto_pair}/{date}", "inputs": ["crypto_pair", "date"]},
    "Options - Snapshot Contract": {"url": "/v3/snapshot/options/{ticker}/{contract}", "inputs": ["ticker", "contract"]},
    "Reference - Market Status": {"url": "/v1/marketstatus/now", "inputs": []}
}

st.set_page_config(page_title="Polygon API Explorer", layout="wide")
st.title("API Data Explorer (Polygon.io)")
st.markdown("---")

# Input API Key
api_key = st.text_input("Inserisci la tua API Key di Polygon", type="password")

if api_key:
    selected = st.selectbox("Seleziona Endpoint", list(ENDPOINTS.keys()))
    config = ENDPOINTS[selected]
    
    st.markdown(f"**Endpoint target:** `{BASE_URL}{config['url']}`")
    
    user_inputs = {}
    
    # Generazione dinamica dei campi di input
    if config["inputs"]:
        cols = st.columns(len(config["inputs"]))
        for i, req_input in enumerate(config["inputs"]):
            with cols[i]:
                if req_input == "date":
                    user_inputs[req_input] = st.date_input("Data (YYYY-MM-DD)").strftime("%Y-%m-%d")
                elif req_input == "crypto_pair":
                    user_inputs[req_input] = st.text_input("Coppia Crypto (es. BTC/USD)").upper()
                elif req_input == "contract":
                    user_inputs[req_input] = st.text_input("ID Contratto (es. O:AAPL270115P00340000)").upper()
                else:
                    user_inputs[req_input] = st.text_input(f"{req_input.capitalize()} (es. AAPL)").upper()
    
    if st.button("Esegui Chiamata API", type="primary"):
        # Validazione input
        if any(not val for val in user_inputs.values()):
            st.error("Errore: Compila tutti i parametri richiesti prima di inviare.")
        else:
            try:
                formatted_path = config["url"].format(**user_inputs)
                full_url = f"{BASE_URL}{formatted_path}?apiKey={api_key}"
                
                with st.spinner("Interrogazione di Polygon in corso..."):
                    response = requests.get(full_url)
                
                # Gestione Risposta e UI Dinamica
                if response.status_code == 200:
                    st.success(f"Status: {response.status_code} OK")
                    data = response.json()
                    
                    st.markdown("### Analisi Dati")
                    
                    if isinstance(data, dict):
                        # 1. Metriche di primo livello
                        top_level_keys = {k: v for k, v in data.items() if not isinstance(v, (dict, list))}
                        if top_level_keys:
                            metrics_cols = st.columns(min(len(top_level_keys), 4))
                            for i, (k, v) in enumerate(top_level_keys.items()):
                                metrics_cols[i % len(metrics_cols)].metric(label=k.capitalize(), value=str(v).upper())
                        
                        st.markdown("---")
                        
                        # 2. Oggetti annidati (es. Status mercati, indici)
                        nested_dicts = {k: v for k, v in data.items() if isinstance(v, dict)}
                        for key, value in nested_dicts.items():
                            with st.expander(f"📌 {key.upper()}", expanded=True):
                                sub_cols = st.columns(min(len(value), 4))
                                for i, (sub_k, sub_v) in enumerate(value.items()):
                                    clean_label = sub_k.replace("_", " ").title()
                                    sub_cols[i % len(sub_cols)].metric(label=clean_label, value=str(sub_v).upper())
                        
                        # 3. Liste di dati (es. Candele storiche, array di risultati)
                        nested_lists = {k: v for k, v in data.items() if isinstance(v, list)}
                        for key, value in nested_lists.items():
                            st.markdown(f"**{key.upper()}**")
                            st.dataframe(value, use_container_width=True)

                    elif isinstance(data, list):
                        st.dataframe(data, use_container_width=True)
                    else:
                        st.write(data)
                else:
                    st.error(f"Errore {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Errore critico durante l'esecuzione: {e}")
else:
    st.info("In attesa dell'API Key per sbloccare l'interfaccia.")
