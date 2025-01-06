import streamlit as st
import requests
import json
from PIL import Image
from io import BytesIO
import time

# Konfiguracja strony
st.set_page_config(page_title="Zdjęcia dla fb/leszno24.pl", layout="wide")

# Inicjalizacja stanu
if 'show_title_input' not in st.session_state:
    st.session_state.show_title_input = False
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'download_data' not in st.session_state:
    st.session_state.download_data = None
if 'current_title' not in st.session_state:
    st.session_state.current_title = ""

def toggle_title_input():
    st.session_state.show_title_input = not st.session_state.show_title_input

def clear_output():
    st.session_state.current_image = None
    st.session_state.download_data = None
    st.session_state.show_title_input = False  # Zamyka pole wprowadzania tytułu

def generate_filename(title):
    """
    Generuje nazwę pliku na podstawie tytułu
    """
    if title == "notitle":
        return "fb_oryginalny.png"
    
    # Podziel tytuł na słowa i weź dwa pierwsze
    words = title.split()
    if len(words) >= 2:
        filename = f"fb_{words[0]}_{words[1]}.png"
    else:
        filename = f"fb_{title}.png"
    
    # Usuń potencjalne niedozwolone znaki z nazwy pliku
    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    return filename.lower()

def send_to_webhook(title):
    """
    Wysyła tytuł do zewnętrznego serwera przez webhook
    """
    webhook_url = "https://hook.eu2.make.com/8o7unp8fi2iurpgx5ivv2wke7ei1d4k2"
    
    payload = {
        "title": title,
        "timestamp": str(time.time())
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        if st.session_state.debug_mode:
            st.write("Wysyłanie danych:", payload)
        
        response = requests.post(
            webhook_url, 
            data=json.dumps(payload),
            headers=headers
        )
        
        if st.session_state.debug_mode:
            st.write("Status odpowiedzi:", response.status_code)
            st.write("Treść odpowiedzi:", response.text)
        
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"message": response.text}
        else:
            st.error(f"Błąd serwera: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Błąd podczas wysyłania: {str(e)}")
        return None

def get_image_from_url(url):
    """
    Pobiera obraz z podanego URL
    """
    try:
        response = requests.get(url)
        if st.session_state.debug_mode:
            st.write("Status pobierania obrazu:", response.status_code)
            st.write("Typ zawartości:", response.headers.get('content-type'))
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Nie udało się pobrać obrazu. Status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Błąd podczas pobierania obrazu: {str(e)}")
        return None

def process_image(title):
    clear_output()  # Czyszczenie poprzednich wyników
    st.session_state.current_title = title  # Zapisz aktualny tytuł
    
    with st.spinner("Przetwarzanie obrazu..."):
        response = send_to_webhook(title)
        
        if response:
            if st.session_state.debug_mode:
                st.write("Odpowiedź serwera:", response)
            
            image_url = None
            if isinstance(response, dict) and 'message' in response:
                image_url = response['message']
            elif isinstance(response, str):
                try:
                    image_url = json.loads(response).get('message')
                except:
                    image_url = response
            
            if image_url:
                if st.session_state.debug_mode:
                    st.write("URL obrazu:", image_url)
                
                image_data = get_image_from_url(image_url)
                if image_data:
                    try:
                        st.session_state.current_image = image_data
                        st.session_state.download_data = image_data
                    except Exception as e:
                        st.error(f"Błąd podczas wyświetlania obrazu: {str(e)}")
            else:
                st.error("Nie znaleziono URL obrazu w odpowiedzi")

def main():
    # Sidebar
    with st.sidebar:
        st.title("Ustawienia")
        st.session_state.debug_mode = st.checkbox("Tryb debugowania")

    # Główny interfejs
    st.title("Zdjęcia dla fb/leszno24.pl")
    
    # Przyciski w jednej linii
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Oryginalny tytuł"):
            process_image("notitle")
            
    with col2:
        st.button(
            "Wprowadź własny tytuł", 
            on_click=toggle_title_input,
            key="custom_title_btn",
            help="Kliknij, aby wprowadzić własny tytuł",
            type="primary"  # jasnozielone tło
        )
    
    # Pole wprowadzania tytułu (ukryte/pokazane)
    if st.session_state.show_title_input:
        custom_title = st.text_input(
            "Wprowadź tytuł, który ma być naniesiony na zdjęcie",
            ""
        )
        if st.button("Generuj zdjęcie z tytułem"):
            if custom_title:
                process_image(custom_title)
            else:
                st.warning("Proszę wprowadzić tytuł!")

    # Wyświetlanie aktualnego obrazu
    if st.session_state.current_image:
        st.image(st.session_state.current_image, caption="Wygenerowany obraz")
        st.download_button(
            label="Pobierz obraz",
            data=st.session_state.download_data,
            file_name=generate_filename(st.session_state.current_title),
            mime="image/png"
        )

if __name__ == "__main__":
    main()