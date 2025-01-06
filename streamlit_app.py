import streamlit as st
<<<<<<< HEAD

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
=======
import requests
import json
import time

st.set_page_config(layout="wide")

# Dodajemy niestandardowy CSS
st.markdown("""
<style>
.stButton>button {
    height: 3rem;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.title("Lista produktów")

# Sidebar
webhook = st.sidebar.text_input("Wprowadź webhook:")
if st.sidebar.button("Zapisz webhook"):
    st.sidebar.success("Webhook zapisany!")

# Inicjalizacja stanu
if 'products' not in st.session_state:
    st.session_state.products = [""]
if 'message' not in st.session_state:
    st.session_state.message = ""
if 'sending' not in st.session_state:
    st.session_state.sending = False

# Funkcje
def add_product():
    if st.session_state.products[-1]:
        st.session_state.products.append("")
    else:
        st.session_state.message = "Wypełnij poprzednie pole!"

def remove_product(index):
    st.session_state.products.pop(index)

def send_products():
    if not webhook:
        st.session_state.message = "Wprowadź webhook w sidebarze!"
        return
    if not any(st.session_state.products):
        st.session_state.message = "Lista produktów jest pusta!"
        return
    st.session_state.sending = True

def clear_products():
    st.session_state.products = [""]

# Interfejs
for i, product in enumerate(st.session_state.products):
    col1, col2 = st.columns([5,1])
    with col1:
        st.session_state.products[i] = st.text_input(f"Produkt {i+1}", value=product, key=f"product_{i}")
    with col2:
        if i > 0 or len(st.session_state.products) > 1:
            st.button("X", key=f"remove_{i}", on_click=remove_product, args=(i,))

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Dodaj kolejny produkt", on_click=add_product)
with col2:
    st.button("Wyślij", on_click=send_products)
with col3:
    if len(st.session_state.products) > 1:
        st.button("Wyczyść", on_click=clear_products)

<<<<<<< HEAD
# Wyświetl nagłówek "Lista produktów" tylko, jeśli jest więcej niż jedno pole
if len(st.session_state.products) > 1 or st.session_state.products[0]:
    st.write("Lista produktów:")
    for product in st.session_state.products:
        st.write(product)
>>>>>>> 712b57f (Initial commit)
=======
# Pole komunikatów
if st.session_state.sending:
    with st.spinner('Ejaj teraz myśli...'):
        time.sleep(1)  # Symulacja opóźnienia
        products = [p for p in st.session_state.products if p]
        response = requests.post(webhook, json={"products": products})
        if response.status_code == 200:
            st.session_state.message = f"{response.text}"
        else:
            st.session_state.message = f"Błąd podczas wysyłania produktów. Kod: {response.status_code}"
        st.session_state.sending = False

if st.session_state.message:
    st.info(st.session_state.message)
    st.session_state.message = ""
>>>>>>> 870c810 ( Changes to be committed:)
