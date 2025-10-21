"""
main.py
Flask web app that shows Pokémon info via PokéAPI

Routes:

- GET/  : Shows the first 151 Pokémon (limit set in first_gen_url variable)
- POST/ : Shows the Pokémon that the user searched for
"""

import requests
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

base_url = "https://pokeapi.co/api/v2/pokemon/"
first_gen_url = "?limit=12"

current_year = datetime.now().year

@app.route("/", methods=["GET", "POST"])
def home():
    """
    This manages the home page depending on the request method.

    GET:
        - Calls Pokéapi with the specified URL and obtains the first 151 Pokémon
        - Each Pokémon has a name, id, type and a sprite

    POST:
        - Allows the user to search for a specific Pokémon by name
        - Calls Pokéapi and obtains the specified Pokémon

    Variables passed to 'index.html':
        -poke_name (str): Name of the Pokémon
        -poke_id (int): Id of the Pokémon
        -poke_type (str): Type of the Pokémon
        -poke_sprite (str): URL of the sprite of the Pokémon
        -pokemon_list (list): List of the Pokémon that will be displayed
        -current year(int): Current year, displayed in the footer
    """

    poke_name = ""
    poke_id = ""
    poke_type = ""
    poke_sprite = ""
    pokemon_list = []
    search_failed = False

    if request.method == "GET":
        try:
            home_url = f"{base_url}{first_gen_url}"
            response = requests.get(home_url)
            response.raise_for_status()
            pokemon_list = response.json().get("results", [])
            detailed_pokemons = []
            search_failed = False

            for pokemon in pokemon_list:
                try:
                    r = requests.get(pokemon['url'])
                    r.raise_for_status()
                    data = r.json()

                    sprite = data.get('sprites', {}).get('front_default')

                    detailed_pokemons.append({
                        'id': data.get('id'),
                        'name': data.get('name').capitalize(),
                        'type': ' '.join([t['type']['name'] for t in data.get('types', [])],),
                        'sprite': sprite
                    })
                except requests.RequestException as e:
                    print(f"Error retrieving data: {e}")

            pokemon_list = detailed_pokemons
        except requests.RequestException as e:
            print(f"Error retrieving data: {e}")

    if request.method == "POST":

        user_pokemon = request.form.get("search").lower()
        try:
            user_url = f"{base_url}{user_pokemon}"
            response = requests.get(user_url)
            if response.status_code == 200:
                pokemon_data = response.json()
                poke_id = pokemon_data.get("id")
                poke_name = pokemon_data.get("name")
                poke_name = poke_name.capitalize()
                types_list = [t['type']['name'] for t in pokemon_data.get('types', [])]
                poke_type = ', '.join(types_list) if types_list else None
                poke_sprite = (pokemon_data.get("sprites") or {}).get("front_default")

            else:
                search_failed = True

        except requests.RequestException:
            search_failed = True
            print("Pokémon not found")

    return render_template("index.html", poke_name=poke_name,
                           poke_id=poke_id,
                           poke_type=poke_type,
                           poke_sprite=poke_sprite,
                           pokemon_list=pokemon_list,
                           current_year=current_year,
                           search_failed=search_failed)

if __name__ == '__main__':
    app.run(debug=True)