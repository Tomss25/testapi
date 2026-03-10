import streamlit as st
import requests

BASE_URL = "https://api.polygon.io"

st.set_page_config(page_title="Asset Dashboard", layout="wide")
st.title("Terminale di Analisi Asset")
st.markdown("---")

# 1. Configurazione
api_key = st.text_input("Inserisci API Key (Polygon.io)", type="password")

# 2. L'unico input che conta
ticker = st.text_input("Inserisci il Ticker dell'Asset (es. AAPL, TSLA, NVDA)").upper()

if api_key and ticker:
    if st.button("Analizza Asset", type="primary"):
        
        # Prepariamo le tre chiamate necessarie per un cruscotto reale
        url_last_trade = f"{BASE_URL}/v2/last/trade/{ticker}?apiKey={api_key}"
        url_prev_close = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={api_key}"
        url_details = f"{BASE_URL}/v3/reference/tickers/{ticker}?apiKey={api_key}"
        
        with st.spinner(f"Costruzione dashboard per {ticker} in corso..."):
            try:
                # Esecuzione delle chiamate
                res_trade = requests.get(url_last_trade)
                res_prev = requests.get(url_prev_close)
                res_details = requests.get(url_details)
                
                # Se l'asset non esiste o la chiave è errata, blocchiamo tutto subito
                if res_trade.status_code != 200:
                    st.error(f"Impossibile recuperare i dati per {ticker}. Verifica il ticker e la chiave API.")
                else:
                    data_trade = res_trade.json()
                    data_prev = res_prev.json()
                    data_details = res_details.json().get("results", {})
                    
                    # --- RENDER DELLA DASHBOARD ---
                    
                    # Intestazione con i dettagli della compagnia
                    st.subheader(f"{data_details.get('name', ticker)} ({ticker})")
                    st.caption(f"Settore: {data_details.get('sic_description', 'N/D')} | Mercato: {data_details.get('primary_exchange', 'N/D')}")
                    
                    st.markdown("### Dati di Mercato")
                    
                    # Estrazione logica dei prezzi
                    last_price = data_trade.get("results", {}).get("p", 0.0)
                    prev_close = data_prev.get("results", [{}])[0].get("c", 0.0)
                    
                    # Calcolo della variazione percentuale (logica di business reale, non solo stampa di JSON)
                    if prev_close > 0:
                        delta = last_price - prev_close
                        delta_pct = (delta / prev_close) * 100
                    else:
                        delta = 0.0
                        delta_pct = 0.0
                        
                    # Visualizzazione con metriche native e colori dinamici
                    col1, col2, col3, col4 = st.columns(4)
                    
                    col1.metric("Ultimo Prezzo", f"${last_price:,.2f}", f"{delta:,.2f} ({delta_pct:.2f}%)")
                    col2.metric("Chiusura Precedente", f"${prev_close:,.2f}")
                    col3.metric("Volume (Ieri)", f"{data_prev.get('results', [{}])[0].get('v', 0):,}")
                    col4.metric("Market Cap", f"${data_details.get('market_cap', 0):,.0f}")
                    
                    st.markdown("---")
                    
                    # Debug tecnico nascosto (se proprio non riesci a fare a meno di guardare il JSON)
                    with st.expander("Mostra Dati Grezzi (JSON)"):
                        st.json({
                            "Last Trade": data_trade,
                            "Previous Close": data_prev,
                            "Ticker Details": data_details
                        })

            except Exception as e:
                st.error(f"Errore critico durante l'elaborazione: {e}")
else:
    if not api_key:
        st.info("Attesa API Key.")
    elif not ticker:
        st.info("Attesa inserimento Ticker.")
