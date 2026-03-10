import streamlit as st
import requests

BASE_URL = "https://api.polygon.io"

st.set_page_config(page_title="Asset Dashboard", layout="wide")
st.title("Terminale di Analisi Asset")
st.markdown("---")

api_key = st.text_input("Inserisci API Key (Polygon.io)", type="password")
ticker = st.text_input("Inserisci il Ticker dell'Asset (es. AAPL, TSLA, NVDA)").upper()

if api_key and ticker:
    if st.button("Analizza Asset", type="primary"):
        
        url_last_trade = f"{BASE_URL}/v2/last/trade/{ticker}?apiKey={api_key}"
        url_prev_close = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={api_key}"
        url_details = f"{BASE_URL}/v3/reference/tickers/{ticker}?apiKey={api_key}"
        
        with st.spinner(f"Costruzione dashboard per {ticker} in corso..."):
            try:
                res_trade = requests.get(url_last_trade)
                res_prev = requests.get(url_prev_close)
                res_details = requests.get(url_details)
                
                # --- BLOCCO DI DEBUG BRUTALE ---
                # Se anche solo una chiamata fallisce, fermiamo tutto e leggiamo i log del server.
                if res_trade.status_code != 200 or res_prev.status_code != 200 or res_details.status_code != 200:
                    st.error("Il server di Polygon ha rifiutato la richiesta. Smettila di tirare a indovinare e leggi questi log:")
                    colA, colB, colC = st.columns(3)
                    colA.error(f"Ultimo Trade: HTTP {res_trade.status_code}\n\n{res_trade.text}")
                    colB.error(f"Chiusura Prec: HTTP {res_prev.status_code}\n\n{res_prev.text}")
                    colC.error(f"Dettagli: HTTP {res_details.status_code}\n\n{res_details.text}")
                    st.stop() # Uccide l'esecuzione del codice qui.
                
                # --- RENDER DELLA DASHBOARD (Se non ci sono errori) ---
                data_trade = res_trade.json()
                data_prev = res_prev.json()
                data_details = res_details.json().get("results", {})
                
                st.subheader(f"{data_details.get('name', ticker)} ({ticker})")
                st.caption(f"Settore: {data_details.get('sic_description', 'N/D')} | Mercato: {data_details.get('primary_exchange', 'N/D')}")
                
                st.markdown("### Dati di Mercato")
                
                last_price = data_trade.get("results", {}).get("p", 0.0)
                prev_close = data_prev.get("results", [{}])[0].get("c", 0.0)
                
                if prev_close > 0:
                    delta = last_price - prev_close
                    delta_pct = (delta / prev_close) * 100
                else:
                    delta = 0.0
                    delta_pct = 0.0
                    
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Ultimo Prezzo", f"${last_price:,.2f}", f"{delta:,.2f} ({delta_pct:.2f}%)")
                col2.metric("Chiusura Precedente", f"${prev_close:,.2f}")
                col3.metric("Volume (Ieri)", f"{data_prev.get('results', [{}])[0].get('v', 0):,}")
                col4.metric("Market Cap", f"${data_details.get('market_cap', 0):,.0f}")
                
                st.markdown("---")
                
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
