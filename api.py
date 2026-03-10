import streamlit as st
import requests
import pandas as pd
from twelvedata import TDClient

st.set_page_config(page_title="Terminale Quantitativo", layout="wide")

# ROUTING DELLE PAGINE NELLA SIDEBAR
st.sidebar.title("Navigazione Provider")
page = st.sidebar.radio("Seleziona API:", ["Polygon.io (Azionario USA)", "Twelve Data (Universale)"])

st.sidebar.markdown("---")
st.sidebar.caption("Attenzione: Inserisci le chiavi per i rispettivi provider per operare.")

if page == "Polygon.io (Azionario USA)":
    st.title("Terminale Polygon.io")
    
    api_key = st.text_input("API Key (Polygon.io)", type="password", key="poly_key")
    ticker = st.text_input("Ticker Asset (es. AAPL)", key="poly_ticker").upper()
    
    if api_key and ticker:
        if st.button("Analizza con Polygon", type="primary"):
            BASE_URL = "https://api.polygon.io"
            url_trade = f"{BASE_URL}/v2/last/trade/{ticker}?apiKey={api_key}"
            url_prev = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={api_key}"
            url_details = f"{BASE_URL}/v3/reference/tickers/{ticker}?apiKey={api_key}"
            
            with st.spinner("Estrazione dati da Polygon..."):
                try:
                    res_trade = requests.get(url_trade)
                    res_prev = requests.get(url_prev)
                    res_details = requests.get(url_details)
                    
                    if res_prev.status_code != 200 or res_details.status_code != 200:
                        st.error("Errore fatale: Impossibile recuperare i dati storici o anagrafici.")
                        st.stop()
                    
                    data_prev = res_prev.json()
                    details = res_details.json().get("results", {})
                    
                    st.subheader(f"{details.get('name', ticker)} ({ticker})")
                    
                    # Estrazione e formattazione dei dati OHLCV che volevi vedere
                    results_array = data_prev.get("results", [])
                    if results_array:
                        raw_data = results_array[0]
                        # Creiamo un dizionario pulito per la tabella
                        clean_data = {
                            "Apertura (o)": raw_data.get("o"),
                            "Massimo (h)": raw_data.get("h"),
                            "Minimo (l)": raw_data.get("l"),
                            "Chiusura (c)": raw_data.get("c"),
                            "Volume (v)": raw_data.get("v"),
                            "VWAP (vw)": raw_data.get("vw"),
                            "Transazioni (n)": raw_data.get("n")
                        }
                        
                        st.markdown("### Dettaglio Giornata Precedente (OHLCV)")
                        # Trasformiamo i dati in un DataFrame orizzontale per una lettura elegante
                        df_prev = pd.DataFrame([clean_data])
                        
                        # Formattazione per la visualizzazione in tabella
                        st.dataframe(
                            df_prev.style.format({
                                "Apertura (o)": "${:.2f}", "Massimo (h)": "${:.2f}", 
                                "Minimo (l)": "${:.2f}", "Chiusura (c)": "${:.2f}", 
                                "VWAP (vw)": "${:.2f}", "Volume (v)": "{:,.0f}", 
                                "Transazioni (n)": "{:,.0f}"
                            }),
                            use_container_width=True, hide_index=True
                        )
                    
                    # Gestione isolata Last Price (Piano Premium)
                    st.markdown("### Prezzo Attuale")
                    if res_trade.status_code == 200:
                        last_p = res_trade.json().get("results", {}).get("p", 0.0)
                        st.metric("Ultimo Scambio (Real-Time)", f"${last_p:,.2f}")
                    else:
                        st.warning("Ultimo Prezzo Real-Time non disponibile (Richiede upgrade piano Polygon).")

                except Exception as e:
                    st.error(f"Errore di sistema: {e}")
    else:
        st.info("Compila API Key e Ticker per iniziare.")

elif page == "Twelve Data (Universale)":
    st.title("Terminale Twelve Data")
    
    api_key_td = st.text_input("API Key (Twelve Data)", type="password", key="td_key")
    ticker_td = st.text_input("Ticker Asset (es. AAPL, EUR/USD, BTC/USD)", key="td_ticker").upper()
    
    col1, col2 = st.columns(2)
    interval = col1.selectbox("Intervallo", ["1min", "5min", "15min", "1h", "1day"])
    outputsize = col2.number_input("Numero di candele", min_value=1, max_value=100, value=12)
    
    if api_key_td and ticker_td:
        if st.button("Estrai Serie Storica", type="primary"):
            with st.spinner(f"Estrazione {outputsize} candele da {interval} per {ticker_td}..."):
                try:
                    td = TDClient(apikey=api_key_td)
                    ts = td.time_series(symbol=ticker_td, interval=interval, outputsize=outputsize)
                    
                    data_json = ts.as_json()
                    
                    if not data_json:
                        st.error("Nessun dato restituito. Verifica il ticker.")
                    elif "code" in data_json and data_json.get("status") == "error":
                        st.error(f"Errore API Twelve Data: {data_json.get('message')}")
                    else:
                        st.success("Dati estratti con successo.")
                        
                        # Twelve Data restituisce un array di dizionari nativamente convertibile in DataFrame Pandas
                        df_td = pd.DataFrame(data_json)
                        
                        st.markdown(f"### Dati Storici {ticker_td} ({interval})")
                        st.dataframe(df_td, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Errore critico: {e}")
    else:
        st.info("Compila API Key e Ticker per iniziare.")
