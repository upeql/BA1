from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'intro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    minutes_parts_123 = 6

    timers = dict(consent=120, workerid=120, welcome=120)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    consent = models.BooleanField(label="Select 'Yes' if you agree to participate. Select 'No' otherwise. ",
                                  choices = [
                                                [True, "Yes"],
                                                [False, "No"],
                                                ])
    workerid = models.StringField(label="")



    timeout = models.BooleanField(initial=False)


# FUNCTIONS
def creating_session(subsession: Subsession):
    for p in subsession.session.get_participants():
        pvars = p.vars
        p.excluded, p.dropout = False, False
        pvars['num_timeouts'] = 0
        #pvars['lottery_choice'], pvars['lottery_win'], p.lottery_payoff = None, None, 0
        p.endowment_payoff, p.penalty_payoff, p.contribution = 0,0,0

# PAGES
class Consent(Page):
    form_model = 'player'
    form_fields = ['consent']

    timeout_seconds = C.timers['consent']
    timer_text = 'Time Remaining: '

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.timeout = True
            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class Disagree(Page):
    # Display this page only if paricipant disagrees with the terms.
    @staticmethod
    def is_displayed(player: Player):
        return player.consent == False

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        player.participant.dropout = True
        return upcoming_apps[-1]


class Prolific_id(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.consent == True

    form_model = 'player'
    form_fields = ['workerid']

    timeout_seconds = C.timers['workerid']
    timer_text = 'Time Remaining: '


    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.timeout = True
            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class Welcome(Page):
    timeout_seconds = C.timers['welcome']
    timer_text = 'Time Remaining: '

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.timeout = True
            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]


page_sequence = [Consent,
                 Disagree,
                 Prolific_id
                 ]
