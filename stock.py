import streamlit as st
import pandas as pd
from itertools import combinations

st.set_page_config(page_title="Stok Optimizasyonu", layout="wide")
st.title("📦 Stok Optimizasyonu Uygulaması")

st.markdown("Bu uygulama, stok boylarını en verimli şekilde kullanarak siparişleri en az fire ile karşılamanı sağlar.")

# --- Stok Girişi ---
st.subheader("1. Stok Bilgileri")
num_stok = st.number_input("Kaç farklı stok uzunluğunuz var?", min_value=1, max_value=20, value=2)

stoklar = []
for i in range(num_stok):
    cols = st.columns([1, 1])
    with cols[0]:
        uzunluk = st.number_input(f"Stok #{i+1} - Uzunluk (metre)", min_value=0.0, step=0.5, format="%.2f", key=f"stok_len_{i}")
    with cols[1]:
        adet = st.number_input(f"Adet", min_value=0, step=1, key=f"stok_qty_{i}")
    if adet > 0:
        stoklar.append({"length": uzunluk, "qty": adet})

# --- Sipariş Girişi ---
st.subheader("2. Sipariş Bilgileri")
num_siparis = st.number_input("Kaç farklı sipariş uzunluğu var?", min_value=1, max_value=100, value=2)

siparisler = []
for i in range(num_siparis):
    cols = st.columns([1, 1])
    with cols[0]:
        uzunluk = st.number_input(f"Sipariş #{i+1} - Uzunluk (metre)", min_value=0.0, step=0.5, format="%.2f", key=f"sip_len_{i}")
    with cols[1]:
        adet = st.number_input(f"Adet", min_value=0, step=1, key=f"sip_qty_{i}")
    if adet > 0:
        siparisler.extend([round(uzunluk, 2)] * adet)

# --- Hesapla Butonu ---
if st.button("📊 Hesapla"):
    if not stoklar or not siparisler:
        st.error("Lütfen geçerli stok ve sipariş verisi girin.")
    else:
        siparisler.sort(reverse=True)

        stock_pool = []
        for s in stoklar:
            stock_pool.extend([s["length"]] * s["qty"])

        results = []
        waste_total = 0

        def best_stock_and_combo(orders, stock_pool, max_comb=6):
            best, best_stock, best_waste = None, None, float("inf")
            for r in range(1, min(len(orders), max_comb) + 1):
                for combo in combinations(orders, r):
                    total = round(sum(combo), 2)
                    for stock in set(stock_pool):
                        if total <= stock:
                            waste = round(stock - total, 2)
                            if (waste < best_waste) or (waste == best_waste and len(combo) > len(best or [])):
                                best, best_stock, best_waste = combo, stock, waste
                                if waste == 0:
                                    return best, best_stock, best_waste
            return best, best_stock, best_waste

        while siparisler and stock_pool:
            combo, chosen_stock, waste = best_stock_and_combo(siparisler, stock_pool)
            if combo:
                for c in combo:
                    siparisler.remove(c)
                stock_pool.remove(chosen_stock)
                results.append((combo, chosen_stock, waste))
                waste_total += waste
            else:
                break

        st.success("Hesaplama tamamlandı!")

        df_result = pd.DataFrame([{
            "Kullanılacak Sipariş Kombinasyonu": " x ".join(map(str, r[0])),
            "Kullanılacak Stok Uzunluğu (Metre)": r[1],
            "Fire (Metre)": r[2]
        } for r in results])

        st.dataframe(df_result, use_container_width=True)
        st.markdown(f"### ♻️ Toplam Fire: {round(waste_total, 2)} metre")

        if siparisler:
            st.warning("Bazı siparişler yerleştirilemedi:")
            st.write(siparisler)

