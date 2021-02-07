import gi, django.contrib.auth.hashers, sys, requests
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.Gdk import Color

class GUI:
    def __init__(self):
        django.contrib.auth.hashers.settings.configure()

        self.builder = Gtk.Builder()
        self.builder.add_from_file('main.ui')
        self.builder.connect_signals(self)

        self.builder.get_object('username').set_text("alvaro")
        self.builder.get_object('password').set_text("entrar123")
        self.builder.get_object('votingId').set_text("1")

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
                    self.voting(user, voting_id)


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
        else:
            self.builder.get_object('votingIdLabelError').set_text("Voting not found")

        return end_date_ok and voting_id_ok

    def voting(self, user, voting_id):
        url = 'http://localhost:8000/voting/?id=' + str(voting_id)
        r = requests.get(url)
        voting = r.json()[0]

        votingWin = VotingWindow(voting)
        votingWin.show_all()
        votingWin.fullscreen()

class VotingWindow(Gtk.Window):
    def __init__(self, voting):
        Gtk.Window.__init__(self, title=str(voting["id"]) + " - " + str(voting["name"]))

        self.box = Gtk.Box(spacing=6, orientation="vertical")
        self.add(self.box)

        self.label = Gtk.Label(label=str(voting["id"]) + " - " + str(voting["name"]))
        self.box.pack_start(self.label, True, True, 0)
        self.label = Gtk.Label(label="Ejemplo de pregunta")
        self.box.pack_start(self.label, True, True, 0)
        radioButton1 = Gtk.RadioButton("Opción 1")
        self.box.pack_start(radioButton1, True, True, 0)
        radioButton2 = Gtk.RadioButton.new_from_widget(radioButton1)
        radioButton2.set_label("Opción 2")
        self.box.pack_start(radioButton2, True, True, 0)
        radioButton3 = Gtk.RadioButton.new_from_widget(radioButton1)
        radioButton3.set_label("Opción 3")
        self.box.pack_start(radioButton3, True, True, 0)
        '''
        self.cur.execute("SELECT question_id from voting_voting_question where voting_id = %s", [voting[0]])
        questionsIdentifiers = self.cur.fetchall()

        questions = []
        questionsOptions = []

        for questionId in questionsIdentifiers:
            self.cur.execute("SELECT * from voting_question where id = %s", [questionId[0]])
            question = self.cur.fetchall()
            questions.append((question[0][0], question[0][1]))

        for q in questions:
            self.cur.execute("SELECT * from voting_questionoption where question_id = %s", [q[0]])
            options = self.cur.fetchall()
            for option in options:
                questionsOptions.append((option[0], option[1], option[2], option[3]))

        for q in questions:
            question_description = Gtk.Label(label="Question: "+str(q[1]))
            self.box.pack_start(question_description, True, True, 0)

            for option in questionsOptions:
                i = 0
                if option[3] == q[0]:
                    if i == 0:
                        radioButton1 = Gtk.RadioButton("Option: "+str(option[0]))
                        self.box.pack_start(radioButton1, True, True, 0)
                    else:
                        radioButton2 = Gtk.RadioButton.new_from_widget(radioButton1)
                        radioButton2.set_label("Option: "+str(option[0]))
                        self.box.pack_start(radioButton2, True, True, 0)
        '''
        sendButton = Gtk.Button.new_with_label("Votar")
        self.box.pack_start(sendButton, True, True, 0)

    def on_logout_clicked(self, window):
        user = []
        Gtk.VotingWindow.destroy()



def main():
    app = GUI()
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
