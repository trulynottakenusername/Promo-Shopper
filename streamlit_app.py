import streamlit as st
<<<<<<< HEAD

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
=======
import requests
from streamlit_modal import Modal

st.title("Witaj, Przemek!")
st.write("To jest twój pierwszy Streamlit web app!")

# Sidebar
st.sidebar.header("Ustawienia")
webhook_url = st.sidebar.text_input("Adres webhook:", "https://your-webhook-url.com")  

if st.sidebar.button("Zapisz"):
    st.session_state.webhook_url = webhook_url
    st.sidebar.success("Webhook zapisany!")

# Inicjalizacja stanu produktów
if 'products' not in st.session_state:
    st.session_state.products = [""]  

def add_product():
    st.session_state.products.append("")  
    st.rerun()  

def clear_products():
    st.session_state.products = [""]  
    st.rerun()  

def remove_product(i):
    del st.session_state.products[i]  
    st.rerun()  

# Wyświetl wszystkie pola do wpisywania produktów
for i in range(len(st.session_state.products)):
    col1, col2 = st.columns((4, 1), vertical_alignment="bottom")
    with col1:
        product_name = st.text_input(f"Podaj nazwę produktu {i+1}:", value=st.session_state.products[i])
        st.session_state.products[i] = product_name
    with col2:
        if product_name:
            if st.button("X", key=f"remove_{i}"):
                remove_product(i)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("+ Dodaj kolejny produkt"):
        if all(product.strip() for product in st.session_state.products):
            add_product()
        else:
            st.modal("Proszę wypełnić wszystkie pola produktów.")
with col2:
    if st.button("Wyślij"):
        if all(product.strip() for product in st.session_state.products):
            webhook_url = st.session_state.get('webhook_url', "https://your-webhook-url.com")  
            data = {"products": st.session_state.products}
            response = requests.post(webhook_url, json=data)
            if response.status_code == 200:
                st.success("Wysłano pomyślnie!")
                st.text_input("Odpowiedź z webhook:", value=response.text, disabled=True)
            else:
                st.error("Błąd przy wysyłaniu danych.")
        else:
            st.modal("Proszę wypełnić wszystkie pola produktów.")
with col3:
    if any(st.session_state.products):
        if st.button("Wyczyść"):
            clear_products()
    else:
        st.write("")  # pusty kontener, aby utrzymać kolumnę

# Wyświetl nagłówek "Lista produktów" tylko, jeśli jest więcej niż jedno pole
if len(st.session_state.products) > 1 or st.session_state.products[0]:
    st.write("Lista produktów:")
    for product in st.session_state.products:
        st.write(product)
>>>>>>> 712b57f (Initial commit)
