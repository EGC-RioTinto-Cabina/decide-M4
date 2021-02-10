import gi, django.contrib.auth.hashers, sys, requests, random, json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.Gdk import Color, RGBA


class GUI:
    def __init__(self):
        django.contrib.auth.hashers.settings.configure()

        self.builder = Gtk.Builder()
        self.builder.add_from_file('main.ui')
        self.builder.connect_signals(self)

        window = self.builder.get_object('window')
        window.show_all()
        window.fullscreen()

    def on_window_destroy(self, window):
        Gtk.main_quit()

    def on_login_clicked(self, button, false=None):

        username = self.builder.get_object('username').get_text()
        password = self.builder.get_object('password').get_text()
        voting_id = self.builder.get_object('votingId').get_text()

        COLOR_INVALID = Color(50000, 0, 0)
        self.builder.get_object('usernameLabelError').modify_fg(Gtk.StateFlags.NORMAL, COLOR_INVALID)
        self.builder.get_object('passwordLabelError').modify_fg(Gtk.StateFlags.NORMAL, COLOR_INVALID)
        self.builder.get_object('votingIdLabelError').modify_fg(Gtk.StateFlags.NORMAL, COLOR_INVALID)

        if not username:
            self.builder.get_object('usernameLabelError').set_text("Empty Username")
        else:
            self.builder.get_object('usernameLabelError').set_text("")

        if not password:
            self.builder.get_object('passwordLabelError').set_text("Empty Password")
        else:
            self.builder.get_object('passwordLabelError').set_text("")

        if not voting_id:
            self.builder.get_object('votingIdLabelError').set_text("Must insert voting identifier")
        else:
            self.builder.get_object('votingIdLabelError').set_text("")

        if username and password and voting_id:
            token = self.login(username, password)

            if token == None:
                print("User not found")
                self.builder.get_object('usernameLabelError').set_text("Invalid user or password")
            else:
                user = self.get_user(token)
                check_voting_access = self.check_voting_access(user, voting_id)

                if check_voting_access:
                    voting = self.find_voting(voting_id)

                    votingWin = VotingWindow(token, user, voting)
                    votingWin.show_all()
                    votingWin.fullscreen()
                else:
                    self.builder.get_object('votingIdLabelError').set_text("Voting not found")

    def login(self, username, password):
        url = 'http://127.0.0.1:8000/gateway/authentication/login/'
        payload = {'username': username, 'password': password}

        r = requests.post(url, data=payload)

        if r.status_code == 200:
            return r.json()["token"]
        else:
            return None

    def get_user(self, token):
        url = 'http://127.0.0.1:8000/gateway/authentication/getuser/'
        payload = {'token': token}

        r = requests.post(url, data=payload)
        return r.json()

    def check_voting_access(self, user, voting_id):
        end_date_ok = False
        voting_id_ok = False

        url = 'http://localhost:8000/voting/?id=' + str(voting_id)
        r = requests.get(url)

        if r.json():
            voting = r.json()[0]

            end_date_ok = voting["end_date"] == None

            url = 'http://localhost:8000/census/' + str(voting["id"]) + '/?voter_id=' + str(user["id"])
            r = requests.get(url)

            voting_id_ok = r.json() == "Valid voter"
            if voting_id_ok == False:
                self.builder.get_object('votingIdLabelError').set_text("You don't have access to this voting")

        return end_date_ok and voting_id_ok

    def find_voting(self, voting_id):
        url = 'http://localhost:8000/voting/?id=' + str(voting_id)
        r = requests.get(url)
        voting = r.json()[0]

        return voting


class VotingWindow(Gtk.Window):
    def __init__(self, token, user, voting):
        Gtk.Window.__init__(self, title=str(voting["id"]) + " - " + str(voting["name"]))

        self.voting = voting
        self.user = user
        self.token = token

        self.box = Gtk.Box(spacing=6, orientation="vertical")
        self.add(self.box)

        self.label = Gtk.Label(label=str(voting["id"]) + " - " + str(voting["name"]))
        self.box.pack_start(self.label, True, True, 0)
        question = voting["question"]
        self.label = Gtk.Label(label=question["desc"])
        self.box.pack_start(self.label, True, True, 0)
        options = question["options"]

        i = 1
        for op in options:
            if i == 1:
                self.radioButton1 = Gtk.RadioButton(op["option"])
                self.box.pack_start(self.radioButton1, True, True, 0)
                self.radioButton1.toggled
            else:
                self.radioButton2 = Gtk.RadioButton.new_from_widget(self.radioButton1)
                self.radioButton2.set_label(op["option"])
                self.box.pack_start(self.radioButton2, True, True, 0)
                self.radioButton2.toggled()

            i = i + 1

        self.sendButton = Gtk.Button.new_with_label("Votar")
        self.sendButton.connect("clicked", self.on_send_button_clicked)
        self.box.pack_start(self.sendButton, True, True, 0)

    def on_radio_button_toggled(self, radiobutton):
        if radiobutton.get_active():
            print("%s is active" % (radiobutton.get_label()))

    def on_send_button_clicked(self, button):
        active = next((
            radio for radio in
            self.radioButton1.get_group()
            if radio.get_active()
        ))

        votingOption = ""
        for op in self.voting["question"]["options"]:
            if op["option"] == active.get_label():
                votingOption = op["number"]

        url = 'http://127.0.0.1:8000/gateway/store/'
        payload = {
            'vote': {'a': self.voting["id"], 'b': votingOption},
            'voting': self.voting["id"],
            'voter': self.user["id"],
            'token': self.token
        }

        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        self.sendButton.set_label(" Conglatulations. Your vote has been sent. \r         Click again to close this window")
        self.sendButton.connect("clicked", self.on_logout_clicked)

    def on_logout_clicked(self, window):
        self.token = ""
        self.destroy()


def main():
    app = GUI()
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
