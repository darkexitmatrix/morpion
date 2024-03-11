import tkinter as tk
import numpy as np
import json
import requests

APP_ID="YOU_APP-KEY"
REST_API_KEY="YOUR_REST_API"
HEADERS = {
    "X-Parse-Application-Id": APP_ID,
    "X-Parse-REST-API-Key": REST_API_KEY,
    "Content-Type": "application/json"
}
class MorpionUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Morpion")
        self.mat = np.zeros((3, 3), dtype=int)
        self.session_id = None
        self.player_number = None
        self.info_label = tk.Label(master, text="'Se connecter'", font=('Consolas', 20))
        self.info_label.grid(row=3, column=0, columnspan=3)
        self.buttons = [[tk.Button(master, text='', font=('Consolas', 40), width=2, height=1,command=lambda i=i, j=j: self.player_move(i, j)) for j in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].grid(row=i, column=j)
                self.buttons[i][j].config(state='disabled')  # Désactive le btn pendant la connexion

        self.connect_button = tk.Button(master, text="Se connecter", font=('Consolas', 20), command=self.check_for_waiting_game)
        self.connect_button.grid(row=4, column=0, columnspan=3)

    def check_for_waiting_game(self): ##Check si il y a une partie si oui execute la fonction join_game sinon  create_new_game
        print("check si il y a une partie...")
        response = requests.get("https://parseapi.back4app.com/classes/YOUR_CLASS", headers=HEADERS, params={"where": json.dumps({"waitingPlayer": True})})
        games = response.json().get("results")
        if games:
            self.join_game(games[0])
        else:
            self.create_new_game()

    def join_game(self, game):# Rejoint une partie existante et mettre à jour `waitingPlayer`
        self.session_id = game["objectId"]
        self.player_number = 2
        self.player_turn = game["player_turn"]
        if self.player_turn == self.player_number:
            self.enable_buttons()
        requests.put(f"https://parseapi.back4app.com/classes/YOUR_CLASS/{self.session_id}",
                     headers=HEADERS,
                     data=json.dumps({"waitingPlayer": False}))
        self.sync_game_state()

    def create_new_game(self):# Créer une nouvelle partie et initialiser `player_turn`
        game_data = {
            "matrix": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            "player_turn": 1,
            "winner": 0,
            "waitingPlayer": True,
            "finished": False
        }
        response = requests.post("https://parseapi.back4app.com/classes/YOUR_CLASS", headers=HEADERS, data=json.dumps(game_data))
        game = response.json()
        self.session_id = game["objectId"]
        self.player_number = 1
        self.player_turn = 1
        self.enable_buttons()
        self.sync_game_state()

    def enable_buttons(self): ##Fonction activé les boutons pour joué
        for row in self.buttons:
            for button in row:
                button.config(state='normal')

    def disable_buttons(self): ## fonction désative les boutons
        for row in self.buttons:
            for button in row:
                button.config(state='disabled')

    def sync_game_state(self): ##Function pour récupéré la matrix et le playerturn et met à jours la matrix
        if self.session_id is None:
            print("Aucun jeu en cours.")
            return
        response = requests.get(f"https://parseapi.back4app.com/classes/YOUR_CLASS/{self.session_id}", headers=HEADERS)
        if response.status_code == 200:
            game_state = response.json()
            current_matrix = game_state.get("matrix", [])
            self.player_turn = game_state.get("player_turn", self.player_turn)
            self.mat = np.array(current_matrix)
            for i in range(3):
                for j in range(3):
                    value = self.mat[i, j]
                    text = 'X' if value == 1 else 'O' if value == 2 else ''
                    self.buttons[i][j].config(text=text, state='disabled' if value != 0 else 'normal')

            if self.player_turn == self.player_number:
                self.enable_buttons()
            else:
                self.disable_buttons()

            self.master.after(2000, self.sync_game_state)
        else:
            print(f"Etat du jeu {response.json()}")

    def update_matrix(self, new_matrix): ###Function pour mettre à jours la matrix dans back4app
        if self.session_id is None:
            print("Erreur : Pas de session de jeu relance")
            return
        matrix_list = new_matrix.tolist()
        data = json.dumps({"matrix": matrix_list})
        response = requests.put(f"https://parseapi.back4app.com/classes/YOUR_CLASS/{self.session_id}",headers=HEADERS, data=data)

        if response.status_code == 200:
            print("Matrice update")
        else:
            print(f"Erreur lors de l'update de la matrice : {response.json()}")

    def player_move(self, i, j): ###fonction pour les mouvement du jouer
        if self.player_number != self.player_turn:
            print("Ce n'est pas votre tour.")
            self.sync_game_state()
            return

        if self.mat[i, j] != 0:
            print("La case est déjà prise.")
            return

        self.update_board(i, j, self.player_number)
        if self.check_winner():
            if self.temp_winner == 1:
                print("Joueur 1 a gagné !")
            elif self.temp_winner == 2:
                print("Joueur 2 a gagné !")
            elif self.temp_winner == 0:
                print("Match nul.")
            return

        new_turn = 2 if self.player_turn == 1 else 1
        self.player_turn = new_turn
        self.update_player_turn(new_turn)

    def update_player_turn(self, new_turn): ###Function pour mettre à jours Player_turn dans la bdd
        if self.session_id is None:
            print("Aucun jeu en cours.")
            return

        data = json.dumps({"player_turn": new_turn})
        response = requests.put(f"https://parseapi.back4app.com/classes/YOUR_CLASS/{self.session_id}", headers=HEADERS,
                                data=data)

        if response.status_code == 200:
            print("Le tour du joueur a été mis à jour.")
            self.player_turn = new_turn
        else:
            print(f"Erreur lors de la mise à jour du tour du joueur: {response.json()}")

    def update_board(self, i, j, player): ##Met à jours l'ui
        self.mat[i, j] = player
        self.buttons[i][j].config(text='X' if player == 1 else 'O', state='disabled')
        self.update_matrix(self.mat)

    def check_winner(self): ###Function qui parcours toutes les combo gagnant possible ou si il y a pas de gagnant
        for player in [1, 2]:
            for i in range(3):
                if np.all(self.mat[i, :] == player) or np.all(self.mat[:, i] == player):
                    self.finish_game(player)
                    return True

            if np.all(np.diag(self.mat) == player) or np.all(np.diag(np.fliplr(self.mat)) == player):
                self.finish_game(player)
                return True

        if not np.any(self.mat == 0):
            self.finish_game(0)
            return True

        return False

    def finish_game(self, winner): ###function pour affiche le joueur gagnant
        self.temp_winner = winner
        message = "Match nul" if winner == 0 else f"Joueur {winner} gagne!"
        self.info_label.config(text=message)
        for row in self.buttons:
            for button in row:
                button.config(state='disabled')

        if self.session_id is not None:
            game_data = {
                "winner": winner,
                "finished": True
            }
            response = requests.put(f"https://parseapi.back4app.com/classes/YOUR_CLASS/{self.session_id}",
                                    headers=HEADERS, data=json.dumps(game_data))
            if response.status_code == 200:
                print("Le jeu a été mis à jour avec succès avec le gagnant et marqué comme terminé.")
            else:
                print(f"Erreur lors de la mise à jour de l'état de fin de jeu: {response.json()}")


def start_morpion_ui():
    root = tk.Tk()
    app = MorpionUI(root)
    root.mainloop()
