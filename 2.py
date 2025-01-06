import streamlit as st
import requests
import json
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Dodaj ten styl CSS na początku pliku lub w odpowiednim miejscu

st.markdown(
    """
    <style>
    .element-container:has(style){display: none;}
    #circle-add {display: none; }
    .element-container:has(#circle-add) {
        #display: none;
        vertical-align:center;    }
    .element-container:has(#circle-add) + div button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        padding: 0px;
        line-height: 40px;
        text-align: center;
        font-size: 44px;
        border: 1px solid purple;        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    .element-container:has(style){display: none;}
    #circle-add {display: none; }
    .element-container:has(#circle-no) {
        #display: none;
        vertical-align:center;    }
    .element-container:has(#circle-no) + div button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        padding: 0px;
        line-height: 40px;
        text-align: center;
        font-size: 44px;
        border: 1px solid red;        }
    </style>
    """,
    unsafe_allow_html=True,
)



st.title("Wyszukiwarka promocji")

# Inicjalizacja stanu
if 'products' not in st.session_state:
    st.session_state.products = [""]
if 'promotions' not in st.session_state:
    st.session_state.promotions = []
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = []
if 'message' not in st.session_state:
    st.session_state.message = ""
if 'sending' not in st.session_state:
    st.session_state.sending = False
if 'show_debug' not in st.session_state:
    st.session_state.show_debug = False
if 'debug_data' not in st.session_state:
    st.session_state.debug_data = None
if 'last_search_results' not in st.session_state:
    st.session_state.last_search_results = None

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
    st.session_state.last_search_results = None  # Reset wyników przy nowym wyszukiwaniu

def clear_products():
    st.session_state.products = [""]

def add_to_shopping_list(item):
    if item not in st.session_state.shopping_list:
        st.session_state.shopping_list.append(item)

def remove_from_promotions(item):
    st.session_state.promotions.remove(item)

def add_all_to_shopping_list():
    for item in st.session_state.promotions:
        add_to_shopping_list(item.get('Promocja', 'Brak informacji o promocji'))
    st.session_state.promotions = []

def remove_from_shopping_list(item):
    st.session_state.shopping_list.remove(item)

# Sidebar
webhook = st.sidebar.text_input("Wprowadź webhook:")
if st.sidebar.button("Zapisz webhook"):
    st.sidebar.success("Webhook zapisany!")

# Zaawansowane opcje w sidebarze
st.sidebar.subheader("Zaawansowane")
st.session_state.show_debug = st.sidebar.checkbox("Pokaż debugowanie")

# Interfejs listy produktów
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

# Obsługa wysyłania i odpowiedzi
if st.session_state.sending:
    with st.spinner('Wyszukiwanie promocji...'):
        time.sleep(1)  # Symulacja opóźnienia
        products = [p for p in st.session_state.products if p]
        response = requests.post(webhook, json={"products": products})
        
        # Zapisz dane debugowania
        st.session_state.debug_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text,
            "content": response.content
        }
        
        result_message = ""
        promotions = []
        
        if response.status_code == 200:
            if response.content:
                try:
                    data = json.loads(response.content)
                    st.session_state.debug_data["decoded_data"] = data
                    if isinstance(data, dict) and 'message' in data:
                        promotions = data['message']['content']['PODSUMOWANIE']
                    elif isinstance(data, list) and len(data) > 0:
                        if data[0].get('Produkt') == "000":
                            result_message = data[0].get('Promocja', 'Brak informacji o promocji')
                        else:
                            promotions = data
                except json.JSONDecodeError as e:
                    result_message = f"Błąd dekodowania JSON: {str(e)}"
            else:
                result_message = "Nie ma promocji na żadny z wyszukiwanych produktów!"
        else:
            result_message = f"Błąd podczas wysyłania produktów. Kod: {response.status_code}"
        
        st.session_state.last_search_results = {
            "promotions": promotions,
            "result_message": result_message
        }
        st.session_state.sending = False
# Wyświetlanie wyników
if st.session_state.last_search_results:
    st.subheader("Wynik wyszukiwania")
    promotions = st.session_state.last_search_results["promotions"]
    result_message = st.session_state.last_search_results["result_message"]
    
    if promotions:
        for promo in promotions:
            col1, col2, col3 = st.columns([1, 6, 1])
            with col1:
                product = promo.get('Produkt', 'Nieznany produkt')
                cena = promo.get('Cena', 'Brak ceny')
                
                if cena == 'Brak promocji':
                    st.markdown('<span id="circle-no"></span>', unsafe_allow_html=True)
                    if st.button("❌", key=f"add_{product}"):
                        pass
                else:
                    st.markdown('<span id="circle-add"></span>', unsafe_allow_html=True)
                    if st.button("➕", key=f"add_{product}"):
                        add_to_shopping_list(promo)
                        st.success(f"Dodano {product} do listy zakupów!")
            
            with col2:
                product = promo.get('Produkt', 'Nieznany produkt')
                cena = promo.get('Cena', 'Brak ceny')
                sklep = promo.get('Sklep', 'Nieznany sklep')
                promocja_days = promo.get('Promocja', 0)
                imageUrl = promo.get('imageUrl', '')
                stara_cena = promo.get('Stara cena', 'Brak informacji')

                if promocja_days == 'Brak':
                    promocja_text = 'Brak informacji o czasie trwania promocji'
                else:
                    promocja_text = f"Jeszcze {int(promocja_days)} dni promocji" if int(promocja_days) > 0 else 'Brak informacji o promocji'

                if cena:
                    st.markdown(f"**{product}** - {cena} zł")

                if cena != 'Brak promocji':
                    st.markdown(f"{sklep} | {promocja_text} | Stara cena: {stara_cena} zł" if stara_cena != 'Brak informacji' else f"{sklep} | Promocja: {promocja_text}")
            
                @st.dialog("Promocja")
                def open_modal(ikona, imageUrl):
                    if imageUrl and imageUrl != 'Brak':  # Check if imageUrl is not empty or 'Brak'
                        st.image(imageUrl, caption='Sprawdź dokładnie! Oni zawsze oszukują!', use_column_width=True)
                    else:
                        st.write("Tutaj powinno być zdjęcie. Nie ma? Peszek. Coś się spusło...")
            with col3:
                ikona = promo.get('Ikona', '')
                imageUrl = promo.get('imageUrl', '')
                if st.button(ikona, key=f"btn_{ikona}_{promo.get('Produkt', '')}"):  # Add unique product name to key
                    open_modal(ikona, imageUrl)
        
        if promotions:
            st.button("DODAJ WSZYSTKIE", on_click=add_all_to_shopping_list)
    elif result_message:
        st.info(result_message)
    else:
        st.info("Nie znaleziono informacji o produktach.")
        
# Sekcja LISTA ZAKUPÓW
if st.session_state.shopping_list:
    st.subheader("LISTA ZAKUPÓW")
    for item in st.session_state.shopping_list:
        col1, col2 = st.columns([5,1])
        with col1:
            st.write(item)
        with col2:
            st.button("X", key=f"remove_shopping_{item}", on_click=remove_from_shopping_list, args=(item,))

if st.session_state.message:
    st.info(st.session_state.message)
    st.session_state.message = ""

# Debugowanie
if st.session_state.show_debug and st.session_state.debug_data:
    st.subheader("Debugowanie")
    st.write("Kod statusu:", st.session_state.debug_data["status_code"])
    st.write("Nagłówki odpowiedzi:", st.session_state.debug_data["headers"])
    st.write("Surowa odpowiedź (text):", st.session_state.debug_data["text"])
    st.write("Surowa odpowiedź (content):", st.session_state.debug_data["content"])
    if "decoded_data" in st.session_state.debug_data:
        st.write("Zdekodowane dane:", st.session_state.debug_data["decoded_data"])
    st.write("Debug: Zawartość last_search_results:")
    st.write(st.session_state.last_search_results)  