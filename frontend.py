import streamlit as st
import requests
import pandas as pd
import datetime

# Konfiguracja API
API_URL = "http://127.0.0.1:8000"

# Ustawienia strony Streamlit
st.set_page_config(page_title="Camping Manager", page_icon="🏕️", layout="wide")
st.title("🏕️ Campsite Manager")

# Pasek boczny (Sidebar) do nawigacji
menu = st.sidebar.radio("Navigation", ["Spots", "Customers", "Reservations"])

if menu == "Spots":
    st.header("Spots Management")

    # 1. POBIERANIE I WYŚWIETLANIE (GET)
    response = requests.get(f"{API_URL}/spots")
    if response.status_code == 200:
        spots_data = response.json()
        if spots_data:
            # Zamieniamy listę słowników na ładną tabelę (DataFrame)
            df = pd.DataFrame(spots_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No spots in database.")
    else:
        st.error("No connection with API server")

    st.divider()

    # Tworzymy dwie kolumny: jedna do dodawania, druga do edycji
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("➕ Add new spot")
        with st.form("add_spot_form"):
            name = st.text_input("Name")
            spot_type = st.selectbox("Typ", ["tent", "camper", "bungalow"])
            price = st.number_input("Price per night", min_value=0.0, step=10.0, format="%.2f")

            submit_add = st.form_submit_button("Add")

            if submit_add:
                new_spot = {"name": name, "type": spot_type, "price": price}
                res = requests.post(f"{API_URL}/spots", json=new_spot)
                if res.status_code == 200:
                    st.success("Spot added!")
                    st.rerun()  # Odświeża stronę, żeby pokazać nową tabelę
                else:
                    st.error("Error while adding to db.")

    with col2:
        st.subheader("✏️ Edit spot")
        if spots_data:
            # Tworzymy listę ID do wyboru w formularzu edycji
            spot_ids = [spot["id"] for spot in spots_data]

            with st.form("edit_spot_form"):
                selected_id = st.selectbox("Choose spot ID to edit", spot_ids)
                st.caption("Wypełnij tylko te pola, które chcesz zmienić:")

                new_name = st.text_input("New name")
                new_type = st.text_input("New type")
                new_price = st.number_input("New price", min_value=0.0, step=10.0)

                submit_edit = st.form_submit_button("Save changes")

                if submit_edit:
                    update_data = {}
                    if new_name.strip(): update_data["name"] = new_name
                    if new_type.strip(): update_data["type"] = new_type
                    if new_price > 0: update_data["price"] = new_price

                    if update_data:
                        res = requests.patch(f"{API_URL}/spots/{selected_id}", json=update_data)
                        if res.status_code == 200:
                            st.success("Spot edited!")
                            st.rerun()
                        else:
                            st.error(f"Edition error: {res.text}")
                    else:
                        st.warning("No edited data.")

elif menu == "Customers":
    st.header("Customers Manager")

    # 1. POBIERANIE I WYŚWIETLANIE (GET)
    response = requests.get(f"{API_URL}/customers")
    if response.status_code == 200:
        customers_data = response.json()
        if customers_data:
            df = pd.DataFrame(customers_data)
            # Zmieniamy kolejność kolumn, żeby ładniej wyglądało, i ukrywamy index
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Brak klientów w bazie. Dodaj pierwszego poniżej!")
    else:
        st.error("Błąd połączenia z serwerem API.")

    st.divider()

    # Dwie kolumny: Dodawanie i Edycja
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("➕ Dodaj nowego klienta")
        with st.form("add_customer_form"):
            first_name = st.text_input("Imię")
            last_name = st.text_input("Nazwisko")
            email = st.text_input("Adres e-mail")
            phone = st.text_input("Numer telefonu")

            submit_add = st.form_submit_button("Dodaj klienta")

            if submit_add:
                # Prosta walidacja na froncie, czy wymagane pola są wypełnione
                if first_name and last_name and email:
                    new_customer = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone
                    }
                    res = requests.post(f"{API_URL}/customers", json=new_customer)
                    if res.status_code == 200:
                        st.success("Klient dodany pomyślnie!")
                        st.rerun()
                    else:
                        # Przechwytujemy błąd z FastAPI (np. "Email occupied!")
                        error_msg = res.json().get("detail", "Nieznany błąd")
                        st.error(f"Błąd: {error_msg}")
                else:
                    st.warning("Imię, nazwisko i email są wymagane!")

    with col2:
        st.subheader("✏️ Edytuj dane klienta")
        if 'customers_data' in locals() and customers_data:
            # Tworzymy słownik, żeby w rozwijanej liście pokazać "Imię Nazwisko (email)" zamiast samego ID
            customer_options = {f"{c['first_name']} {c['last_name']} ({c['email']})": c["id"] for c in customers_data}

            with st.form("edit_customer_form"):
                selected_label = st.selectbox("Wybierz klienta do edycji", list(customer_options.keys()))
                selected_id = customer_options[selected_label]

                st.caption("Wypełnij tylko te pola, które chcesz zmienić:")

                new_first = st.text_input("Nowe imię (zostaw puste, aby nie zmieniać)")
                new_last = st.text_input("Nowe nazwisko (zostaw puste, aby nie zmieniać)")
                new_email = st.text_input("Nowy e-mail (zostaw puste, aby nie zmieniać)")
                new_phone = st.text_input("Nowy telefon (zostaw puste, aby nie zmieniać)")

                submit_edit = st.form_submit_button("Zapisz zmiany")

                if submit_edit:
                    update_data = {}
                    if new_first.strip(): update_data["first_name"] = new_first
                    if new_last.strip(): update_data["last_name"] = new_last
                    if new_email.strip(): update_data["email"] = new_email
                    if new_phone.strip(): update_data["phone"] = new_phone

                    if update_data:
                        res = requests.patch(f"{API_URL}/customers/{selected_id}", json=update_data)
                        if res.status_code == 200:
                            st.success("Dane klienta zaktualizowane!")
                            st.rerun()
                        else:
                            error_msg = res.json().get("detail", "Nieznany błąd")
                            st.error(f"Błąd edycji: {error_msg}")
                    else:
                        st.warning("Nie wprowadzono żadnych zmian.")


elif menu == "Reservations":
    st.header("Manage Reservations")

    # Pobieramy klientów i miejsca z API, aby pokazać je w formularzach (zamiast samych numerów ID)
    spots_req = requests.get(f"{API_URL}/spots")
    customers_req = requests.get(f"{API_URL}/customers")

    spots_data = spots_req.json() if spots_req.status_code == 200 else []
    customers_data = customers_req.json() if customers_req.status_code == 200 else []

    # Tworzymy słowniki do list rozwijanych { "Wyświetlana nazwa": ID }
    spot_options = {f"{s['name']} ({s['type']})": s["id"] for s in spots_data}
    customer_options = {f"{c['first_name']} {c['last_name']}": c["id"] for c in customers_data}

    # 1. POBIERANIE I WYŚWIETLANIE (GET)
    response = requests.get(f"{API_URL}/reservations")
    if response.status_code == 200:
        reservations_data = response.json()
        if reservations_data:
            df = pd.DataFrame(reservations_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No reservations found. Add your first one below!")
    else:
        st.error("Failed to connect to the API.")

    st.divider()

    # Zabezpieczenie: Nie można dodać rezerwacji, jeśli w bazie nie ma klientów lub miejsc
    if not spots_data or not customers_data:
        st.warning("⚠️ You need to add at least one Spot and one Customer before creating a reservation.")
    else:
        col1, col2 = st.columns(2)

        # DODAWANIE REZERWACJI
        with col1:
            st.subheader("➕ Add new reservation")
            with st.form("add_reservation_form"):
                selected_customer = st.selectbox("Select Customer", list(customer_options.keys()))
                selected_spot = st.selectbox("Select Spot", list(spot_options.keys()))

                # Pola wyboru daty
                start_date = st.date_input("Start Date", value=datetime.date.today())
                end_date = st.date_input("End Date", value=datetime.date.today() + datetime.timedelta(days=1))

                submit_add = st.form_submit_button("Add Reservation")

                if submit_add:
                    if start_date >= end_date:
                        st.error("End date must be strictly after the start date!")
                    else:
                        new_reservation = {
                            "customer_id": customer_options[selected_customer],
                            "spot_id": spot_options[selected_spot],
                            "start_date": str(start_date),
                            "end_date": str(end_date)
                        }
                        res = requests.post(f"{API_URL}/reservations", json=new_reservation)
                        if res.status_code == 200:
                            st.success("Reservation added successfully!")
                            st.rerun()
                        else:
                            error_msg = res.json().get("detail", "Unknown error")
                            st.error(f"Error: {error_msg}")

        # EDYCJA REZERWACJI
        with col2:
            st.subheader("✏️ Edit reservation")
            if 'reservations_data' in locals() and reservations_data:

                # Tworzymy opcje rezerwacji do wyboru.
                # Tutaj formularz jest nieco inny - selectbox jest POZA blokiem st.form,
                # abyśmy mogli dynamicznie załadować aktualne daty do kalendarza na dole.
                res_options = {f"Reservation #{r['id']}": r for r in reservations_data}
                selected_res_label = st.selectbox("Select reservation to edit", list(res_options.keys()))
                selected_res = res_options[selected_res_label]

                with st.form("edit_reservation_form"):
                    st.caption("Update the status and dates below:")

                    # Parsujemy daty z API z powrotem do obiektów Pythonowych, żeby wsadzić je w kalendarz
                    try:
                        curr_start = datetime.date.fromisoformat(selected_res['start_date'])
                        curr_end = datetime.date.fromisoformat(selected_res['end_date'])
                    except (ValueError, TypeError):
                        curr_start = datetime.date.today()
                        curr_end = datetime.date.today() + datetime.timedelta(days=1)

                    # Możliwość zmiany statusu (confirmed, cancelled, completed)
                    status_list = ["confirmed", "cancelled", "completed"]
                    curr_status = selected_res.get("status", "confirmed")
                    status_index = status_list.index(curr_status) if curr_status in status_list else 0

                    new_status = st.selectbox("Status", status_list, index=status_index)
                    new_start = st.date_input("New Start Date", value=curr_start)
                    new_end = st.date_input("New End Date", value=curr_end)

                    submit_edit = st.form_submit_button("Save changes")

                    if submit_edit:
                        if new_start >= new_end:
                            st.error("End date must be strictly after the start date!")
                        else:
                            update_data = {
                                "status": new_status,
                                "start_date": str(new_start),
                                "end_date": str(new_end)
                            }
                            res = requests.patch(f"{API_URL}/reservations/{selected_res['id']}", json=update_data)
                            if res.status_code == 200:
                                st.success("Reservation updated!")
                                st.rerun()
                            else:
                                error_msg = res.json().get("detail", "Unknown error")
                                st.error(f"Error: {error_msg}")