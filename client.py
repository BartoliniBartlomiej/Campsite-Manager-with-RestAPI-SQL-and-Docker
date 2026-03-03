import requests

API_URL_SPOTS = "http://127.0.0.1:8000/spots"
API_URL_CUSTOMERS = "http://127.0.0.1:8000/customers"


def create_spot():
    print("=== Add new camping spot ===")

    name = input("Name: ")
    spot_type = input("Type (tent/camper/etc): ")
    price = float(input("Price per night: "))

    data = {
        "name": name,
        "type": spot_type,
        "price": price
    }

    try:
        response = requests.post(API_URL_SPOTS, json=data)
        response.raise_for_status()

        print("\nSpot successfully added!")
        print("Response from server:")
        print(response.json())

    except requests.exceptions.RequestException as e:
        print("Error while sending request:", e)


def create_customer():
    print("=== Add new customer ===")

    first_name = input("First name: ")
    last_name = input("Last name: ")
    email = input("Email address: ")
    phone = input("Phone number: ")

    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone
    }

    try:
        response = requests.post(API_URL_CUSTOMERS, json=data)
        response.raise_for_status()

        print("\nCustomer successfully added!")
        print("Response from server:")
        print(response.json())

    except requests.exceptions.RequestException as e:
        print("Error while sending request:", e)


if __name__ == "__main__":
    print("\033[H\033[J", end="")
    print("=== Campsite Manager ===")
    print("1. New spot")
    print("2. New customer")
    print("3. New reservation")
    choice = int(input("Choice: "))
    if choice == 1:
        create_spot()
    if choice == 2:
        create_customer()
