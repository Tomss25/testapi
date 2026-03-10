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
                
                # Se falliscono i dati storici o anagrafici, fermiamo l'esecuzione
                if res_prev.status_code != 200 or res_details.status_code != 200:
                    st.error("Errore critico: Impossibile recuperare l'anagrafica o la chiusura precedente. Verifica il ticker e la chiave API.")
                    st.stop()
                
                # Estrazione dati sicuri
                data_prev = res_prev.json()
                data_details = res_details.json().get("results", {})
                
                st.subheader(f"{data_details.get('name', ticker)} ({ticker})")
                st.caption(f"Settore: {data_details.get('sic_description', 'N/D')} | Mercato: {data_details.get('primary_exchange', 'N/D')}")
                
                st.markdown("### Dati di Mercato")
                
                prev_close = data_prev.get("results", [{}])[0].get("c", 0.0)
                volume = data_prev.get("results", [{}])[0].get("v", 0)
                market_cap = data_details.get("market_cap", 0)
                
                # Gestione dell'errore 403 in modo isolato
                if res_trade.status_code == 200:
                    last_price = res_trade.json().get("results", {}).get("p", 0.0)
                    delta = last_price - prev_close
                    delta_pct = (delta / prev_close) * 100 if prev_close > 0 else 0.0
                    price_display = f"${last_price:,.2f}"
                    delta_display = f"{delta:,.2f} ({delta_pct:.2f}%)"
                else:
                    price_display = "Dato Premium (403)"
                    delta_display = "N/D"
                    
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Ultimo Prezzo (Real-Time)", price_display, delta_display)
                col2.metric("Chiusura Precedente", f"${prev_close:,.2f}")
                col3.metric("Volume (Ieri)", f"{volume:,}")
                col4.metric("Market Cap", f"${market_cap:,.0f}")
                
                st.markdown("---")
                
                # Debug tecnico espandibile
                with st.expander("Mostra Log di Sistema e Dati Grezzi"):
                    st.json({
                        "Status Last Trade": res_trade.status_code,
                        "Status Prev Close": res_prev.status_code,
                        "Status Details": res_details.status_code,
                        "Last Trade Raw": res_trade.json() if res_trade.status_code == 200 else res_trade.text,
                        "Previous Close": data_prev,
                        "Ticker Details": data_details
                    })

            except Exception as e:
                st.error(f"Errore critico di sistema: {e}")
else:
    if not api_key:
        st.info("Attesa API Key.")
    elif not ticker:
        st.info("Attesa inserimento Ticker.")
