import streamlit as st
import requests

BASE_URL = "https://api.polygon.io"

# Mappatura strategica: URL path e i parametri esatti che richiedono.
# Se vuoi aggiungere altri endpoint dalla tua lista originale, DEVI seguire questa struttura.
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

# Sicurezza di base: l'API key viene passata a runtime. 
# NON HARDCODARLA MAI QUI DENTRO SE PUBBLICHI SU GITHUB.
api_key = st.text_input("Inserisci la tua API Key di Polygon", type="password")

if api_key:
    selected = st.selectbox("Seleziona Endpoint", list(ENDPOINTS.keys()))
    config = ENDPOINTS[selected]
    
    st.markdown(f"**Endpoint target:** `{BASE_URL}{config['url']}`")
    
    user_inputs = {}
    
    # Generazione dinamica dell'interfaccia basata sui requisiti dell'endpoint
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
        # Controllo che l'utente non invii campi vuoti
        if any(not val for val in user_inputs.values()):
            st.error("Errore: Compila tutti i parametri richiesti prima di inviare.")
        else:
            try:
                # Iniezione dei parametri nel path
                formatted_path = config["url"].format(**user_inputs)
                full_url = f"{BASE_URL}{formatted_path}?apiKey={api_key}"
                
                with st.spinner("Interrogazione di Polygon in corso..."):
                    response = requests.get(full_url)
                
                if response.status_code == 200:
                    st.success(f"Status: {response.status_code} OK")
                    st.json(response.json())
                else:
                    st.error(f"Errore {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Errore critico durante l'esecuzione: {e}")
else:
    st.info("In attesa dell'API Key per sbloccare l'interfaccia.")
