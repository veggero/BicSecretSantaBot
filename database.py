# -*- coding: utf-8 -*-
import os
import csv
import copy
import json
import random 

class User:
    """Represents an user. 
    """
    def __init__(self, username="", address="", message="", status="", **kwargs):
        self.username = username
        self.address = address
        self.message = message
        self.status = ""

    def reset_status(self):
        self.status = ""

class RegisteredDatabase:
    """
    Stores the data regarding the registered users, i.e. their username and address.
    """

    def __init__(self, path_to_db, path_to_settings, path_to_santas="assignments.json"):
        """Initialize the database with the data stored at path_to_db.

        Args:
            path_to_db (string): path to a .csv file containing the usernames of registered, their address and the message that they want to leave to the Secret Santa.
            path_to_settings (string): path to a .csv file containing the settings of the database (readonly or write).
        Side-effects:
            self._users (dict(string, string)): contains the username of reigstered users and their address.
        """
        self._path_to_settings = path_to_settings
        self._path_to_db = path_to_db
        self._path_to_santas = path_to_santas
        self._users={}
        self._santas = {}
        self._can_add_modify_user=False
        self._users_from_dir()
        self._santas_from_file()
        self._settings_from_csv()

    def _settings_from_csv(self):
        """Read a boolean from the setting file, indicating whether we can still modify the users or not.

        Args:
            path (string): path to the boolean saying whether we can modify the users or not.
        Side-effects:
            self._can_add_modify_user is set to what is stored in the settings csv file.
        """
        with open(self._path_to_settings) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for line in csv_reader:
                self._can_add_modify_user = line[0] == "True"
                break

    def _csv_from_settings(self):
        """Dumps the current settings (self._can_add_modify_user) to self._path_to_settings.
        """
        with open(self._path_to_settings, "w") as csv_file:
            csv_file.write("%s"%self._can_add_modify_user)

    def _users_from_dir(self):
        """Load the users from a .json file at self._path_to_db.

        Side-effects:
            self._users (dict(string, string)): contains the username of reigstered users, their address/message/status.
        """
        for fp in os.listdir(self._path_to_db):
            if fp.endswith(".json"):
                path = f'{self._path_to_db}/{fp}'
                with open(path, "r") as f_user:
                    user = User(**json.load(f_user))
                    self._users[user_dict["username"]] = user
        
    def _dir_from_users(self):
        """Dump self._users to a .json file.
        """
        for username in self._users:
            path = f'{self._path_to_db}/{username}.json'
            with open(path, "w") as fp:
                json.dump(self._users[username], fp, default=lambda o: o.__dict__)

    def _update_user_db(self, username):
        """Update the data in the database regarding the user username.

        Args:
            username (string): the user-s Telegram username.
        """
        path = f'{self._path_to_db}/{username}.json'
        with open(path, "w") as fp:
            json.dump(self._users[username], fp, default=lambda o: o.__dict__)

    def _remove_user_db(self, username):
        """Update the data in the database regarding the user username.

        Args:
            username (string): the user-s Telegram username.
        """
        path = f'{self._path_to_db}/{username}.json'
        os.remove(path)
            
    def update_settings(self):
        """Dumps the current settings to the database.
        """
        self._csv_from_settings()
        self._settings_from_csv()

    def _santas_from_file(self):
        """Initialize self._santas from the json file saved at self._path_to_santas.

        Side-effects:
            self._santas contains the match between a santa and their child.
        """
        with open(self._path_to_santas, "r") as fp:
            self._santas = json.load(fp)
    
    def _file_from_santas(self):
        """Dump self._santas to a .json file at self._path_to_santas.

        Side-effects:
            toggles the settings such that it is not possible to add new users or modify them.
        
        Returns:
            (string): a message stating the effect of the setting change.
        """
        with open(self._path_to_santas, "w") as fp:
            json.dump(self._santas, fp)
        msg = self.set_registrations(False)
        self.update_settings() 
        return msg

    def save_santas(self):
        """
        Dump the santas to file.
        """
        msg = self._file_from_santas()
        self._santas_from_file()
        return msg

    def get_child(self, username):
        """Get the child that was assigned to this santa. 

        Args:
            username (string): the user's Telegram username.
        Returs:
            string: a string containing the assigned's user information.
        """
        msg = ""
        if not self._santas:
            msg = "Sembra che le assegnazioni non siano ancora avvenute!\n"
            if username not in self._users:
                # Not registered
                msg += "Sei ancora in tempo per registrarti, usa il comando /register!\n"
            elif not self._users[username].address:
                msg += "Ricordati di aggiornare il tuo indirizzo! \n"
                msg += "Queste sono le informazioni che ho su di te: "+self.print_user_info(username)
                msg += "Pazienta ancora un po', le assegnazioni dovrebbero avvenire il 2 Dicembre. \n"
            else:
                msg += "Pazienta ancora un po', le assegnazioni dovrebbero avvenire il 2 Dicembre. \n"
            return msg
        elif not username in self._santas:
            msg = "Sembra che non ti sia stato assegnato nessuno. Avevi inserito tutte le informazioni necessarie?\n"
        else:
            msg += "Queste sono le informazioni dell'utente che ti è stato assegnato!\n" + self.print_other_user_info(self._santas[username])
            msg += "\nE' una persona davvero speciale, buona fortuna!\n"
        return msg

    def get_incomplete_users(self):
        """Return the usernames of the user that haven't registered an address yet.

        Returns:
            string: a message with the username of the users that still need to provide an address.
        """
        msg = ""
        not_valid = [user.username for user in self._users.values() if not user.address]
        n_tot = len(self._users)
        n_valid = n_tot-len(not_valid) 
        msg += f'{n_valid}/{n_tot} utenti hanno inserito il loro indizzo.\n'

        if n_valid < 2:
            msg += "Non sono sufficienti per procedere alle assegnazioni."

        if not_valid:
            msg += ",".join("@"+username for username in not_valid)
            msg += "\n non hanno ancora inserito il loro indirizzo. \n" #TODO singular/plural
        
        return msg

    def assign_santas(self):
        """Assign each user to their secret-children and dump this information to disk.

        Disable the possibility to add/modify users.

        Returns:
            string: a string stating whether the assignement was successful.
        """
        if len(self._users.keys()) < 2:
            return "Mi spiace ma sono necessarie almeno 2 persone per procedere alle assegnazioni 😔\n"
        if self._santas:
            return "Le assegnazioni erano già state effettuate!\n Per scoprire a chi dovrai fare il regalo usa il comando /assign_me"

        # Retain only users that have an address
        users = [user.username for user in self._users.values() if user.address]
        not_valid = [user.username for user in self._users.values() if not user.address]

        self.set_registrations(False)
        randomized_list = copy.deepcopy(users)
        while True:
            random.shuffle(randomized_list)
            for a, b in zip(users, randomized_list):
                if a == b:
                    break
            else:
                break 
        for santa, child in zip(users, randomized_list):
            self._santas[santa] = child
        msg = "Congratulazioni! Sono state appena effettuate le assegnazioni casuali dei Secret Santa!🎁🎁\n"
        msg += self.save_santas()
        if not_valid:
            msg += ",".join(user for user in not_valid) + " sono stati esclusi in quanto non avevano indicato un indirizzo.\n"
        return msg

    def add_user(self, username):
        """ Add an user to the list of users taking part in the Secret Santa.
        Args:
            username (string): the user's Telegram username.

        Returns:
            string: a message stating whether the registration was successful.
        """
        if not self._can_add_modify_user:
            return "Mi spiace ma non è più possibile aggiungersi al Secret Santa o modificare i dati 😭."

        reply = ""
        if username in self._users.keys():
            reply = "Sembra che tu sia già registrato! \n"
        else:
            user = User(username)
            self._users[username] = user
            self._update_user_db(username)
            reply = "Congratulazioni! Sei stato correttamente aggiunto alla lista di utenti nel Secret Santa🎁. \n"
        reply += "Questi sono i dati che abbiamo su di te:\n" + self.print_user_info(username)
        reply += "Se vuoi essere rimosso dalla lista dei partecipanti, usa il comando /delete_me.\n"
        return reply
    
    def add_address(self, username, address):
        """Records the address of an user.

        Args:
            username (string): user's Telegram username.
            address (string): their address.
        Return:
            string: a message stating whether the operation was successful.
        """
        if not self._can_add_modify_user:
            return "Mi spiace ma non è più possibile aggiungersi al Secret Santa o modificare i dati 😭.\n"

        reply = ""
        if not username in self._users.keys():
            reply = "Non eri presente tra gli utenti registrati per il Secret Santa 🕵️‍♂️. \n"
            reply+= "Se vuoi registrarti usa il comando /register \n"
        else:
            self._users[username].address = address
            self._update_user_db(username)
            reply = "Il tuo indirizzo è stato correttamente aggiornato.\n"
        reply+="Queste sono le informazioni che abbiamo su di te: \n"+self.print_user_info(username)
        return reply

    def add_message(self, username, message):
        """Adds a message that will be displayed to the user's secret santa.

        Args:
            username (string): user's Telegram username.
            message (string): a message to be displayed to their secret santa.

        Returns:
            string: a message stating whether the message was successfully updated.
        """
        if not self._can_add_modify_user:
            return "Mi spiace ma non è più possibile aggiungersi al Secret Santa o modificare i dati 😭.\n"

        reply = ""
        if not username in self._users.keys():
            reply = "Non sei presente tra gli utenti registrati per il Secret Santa 🕵️‍♂️. \n"
            reply+= "Se vuoi registrarti usa il comando /register\n"
        else:
            self._users[username].message = message
            self._update_user_db(username)
            reply = "Il tuo messaggio al Secret Santa è stato correttamente aggiornato.\n"
        reply+="Queste sono le informazioni che abbiamo su di te: \n"+self.print_user_info(username)
        return reply

    def remove_user(self, username):
        """Remove an user to the list of registered users.

        Args:
            username (string): the user's Telegram username. 

        Returns:
            string: a message stating whether the user was successfully removed.
        """
        if not self._can_add_modify_user:
            return "Mi spiace ma non è più possibile aggiungersi al Secret Santa o modificare i dati 😭.\n"

        reply = ""
        if not username in self._users:
            reply = "Non eri presente tra gli utenti registrati per il Secret Santa 🕵️‍♂️.\n"
        else:
            del self._users[username]
            self._remove_user_db(username)
            reply = "Sei stato correttamente eliminato dagli utenti che partecipano al Secret Santa 😢.\n"
        reply += "Queste sono le informazioni che abbiamo su di te: \n"+self.print_user_info(username)
        return reply
    
    def toggle_registrations(self):
        """Toggle whether it is possible to add users or not.

        Side-effects:
            self._can_add_modify_user becomes False if it was True, and True if it was False. 
        
        Returns:
            string: a message stating whether it is possible or not to add/modify users.
        """
        self._can_add_modify_user = not self._can_add_modify_user
        if self._can_add_modify_user:
            reply = "E' ora possibile aggiungere e modificare i dati relativi agli utenti registrati al Secret Santa.\n"
        else:
            reply = "Non è più possibile aggiungere e modificare i dati relativi agli utenti registrati al Secret Santa.\n"
        self.update_settings()
        return reply

    def set_registrations(self, on):
        """Set whether it is possible to add/modify users or not.

        Args:
            on (bool): whether it is possible to add/modify users or not.

        Side-effects:
            self._can_add_modify_user becomes False if it was True, and True if it was False. 
        
        Returns:
            string: a message stating whether it is possible to add/modify user's information.
        """
        self._can_add_modify_user = on
        if self._can_add_modify_user:
            reply = "E' ora possibile aggiungere e modificare i dati relativi agli utenti registrati al Secret Santa.\n"
        else:
            reply = "Non è più possibile aggiungere e modificare i dati relativi agli utenti registrati al Secret Santa.\n"
        self.update_settings()
        return reply

    def get_user_list_msg(self):
        """Rerturn the list of usernames of the registered users.

        Returns:
            string: a message containing the list of registered users.
        """
        if not self._users.keys():
            return "Sii il primo a registrarti per il Secret Santa! 🎁🎁\n"
        msg = '-' + "-".join("@"+username+"\n" for username in self._users.keys())
        return msg
    
    def get_user_list(self):
        """Return the list of registered users.

        Returns:
            [list(string)]: list of the usernames of the registered users.
        """
        return [*self._users]

    def is_registered(self, username):
        """Check if an user is registered.

        Args:
            username (string): the user's username.

        Returns:
            bool: True if the user is registered, false otherwise.
        """
        return username in self._users
    
    def print_other_user_info(self, username):
        """Print the information about another user (intended after santas assignment).

        Args:
            username (string): the name of the other user.
        Returns:
            string: a message containing the information of the user username.
        """
        reply = ""
        if not username in self._users.keys():
            reply = f"OH oh! Qualcosa è andato storto! Non conosco { username }\n" \
                    "E' Colpa di quel cane del programmatore. Digliene due ! \n"
            return reply 
        reply = "👤: " + username + "\n"
        addr = self._users[username].address
        msg = self._users[username].message 
        if not addr:
            reply = f"OPS! Sembra che {username} non abbia inserito un indirizzo. " \
                    "Questo non sarebbe dovuto succedere!\n"
        else:
            reply += "🏠 :" + addr + "\n" 
        if msg:
            reply += "📬: " + msg + "\n"
        return reply
        

    def print_user_info(self, username):
        """Print calling user information. Intended to be used to print an user's own info.

        Args:
            username (string): an user username.

        Returns:
            string: the information of the user.
        """
        reply = ""
        if not username in self._users.keys():
            reply = "Non sei registrato al Secret Santa.\n"
            return reply
    
        reply = "👤: " + username + "\n"
        addr = self._users[username].address
        msg = self._users[username].message 
        if msg:
            reply+="📬: " + msg + "\n"
        else:
            reply+="Puoi aggiungere un messaggio da lasciare al Secret Santa con usando il comando /add_message\n"
        if addr:
            reply+="🏠 :" + addr + "\n" 
            reply+="Assicurati che l'indirizzo sia corretto, e che includa il tuo nome e cognome in caso non sia ovvio da Telegram. \n"
            reply+= "puoi modificarlo con il comando /modify_address \n"
        else:
            reply+="Ricordati che per partecipare al Secret Santa dovrai fornire il tuo indirizzo che includa il tuo nome e cognome in caso non sia ovvio da Telegram. \n"
            reply+="Aggiungilo con il comando /add_address \n"
            reply+= "questa informazione verrà comunicata solo al tuo Secret Santa!\n"
        return reply

    def reset_user_status(self, username):
        """Reset the user status putting it to None.

        Args:
            username (string): the user's Telegram username. 
        """
        if not username in self._users: return 
        self._users[username].reset_status()
    
    def set_user_status(self, username, status):
        """Set the user status to status.

        Args:
            username (string): the user's Telegram username. 
        """
        if not self._can_add_modify_user:
            return "Mi spiace ma non è più possibile aggiungersi al Secret Santa o modificare i dati 😭."

        if not username in self._users:
            return "Sembra che tu non sia tra i partecipanti al Secret Santa. Iscriviti con il comando /register"
        
        self._users[username].status = status
        msg = "Ok! Scrivi qui " \
              ("il tuo indirizzo " if status == "address" else "il messaggio che vuoi lasciare al Secret Santa")
        return msg

    def get_user_status(self, username):
        """Get the user status.

        Args:
            username (string): the user's Telegram username.

        Returns:
            string: the user status. 
        """
        if not username in self._users: return ""
        return self._users[username].status
