from otree.api import *
from random import randint

doc = """
Social Value Orientation by R.Murphy, K.Ackermann, M.Hangraaf:
Murphy, R. O., Ackermann, K. A., & Handgraaf, M. J. J. (2011).
Measuring Social Value Orientation. Judgment and Decision Making, 6(8), 771-781,
see more detailed information: http://vlab.ethz.ch/styled-2/index.html
"""


class C(BaseConstants):
    NAME_IN_URL = 'svo'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # papercups_template = __name__ + '/papercups.html'
    # contact = 'svo/contact.html'
    # minutes_for_svo = 3

    svo_values = dict(
        C11=[85, 85, 85, 85, 85, 85, 85, 85, 85],
        C21=[85, 76, 68, 59, 50, 41, 33, 24, 15],
        C12=[85, 87, 89, 91, 93, 94, 96, 98, 100],
        C22=[15, 19, 24, 28, 33, 37, 41, 46, 50],
        C13=[50, 54, 59, 63, 68, 72, 76, 81, 85],
        C23=[100, 98, 96, 94, 93, 91, 89, 87, 85],
        C14=[50, 54, 59, 63, 68, 72, 76, 81, 85],
        C24=[100, 89, 79, 68, 58, 47, 36, 26, 15],
        C15=[100, 94, 88, 81, 75, 69, 63, 56, 50],
        C25=[50, 56, 63, 69, 75, 81, 88, 94, 100],
        C16=[100, 98, 96, 94, 93, 91, 89, 87, 85],
        C26=[50, 54, 59, 63, 68, 72, 76, 81, 85],
        C17=[100, 96, 93, 89, 85, 81, 78, 74, 70],
        C27=[50, 56, 63, 69, 75, 81, 88, 94, 100],
        C18=[90, 91, 93, 94, 95, 96, 98, 99, 100],
        C28=[100, 99, 98, 96, 95, 94, 93, 91, 90],
        C19=[100, 94, 88, 81, 75, 69, 63, 56, 50],
        C29=[70, 74, 78, 81, 85, 89, 93, 96, 100],
        C110=[100, 99, 98, 96, 95, 94, 93, 91, 90],
        C210=[70, 74, 78, 81, 85, 89, 93, 96, 100],
        C111=[70, 74, 78, 81, 85, 89, 93, 96, 100],
        C211=[100, 96, 93, 89, 85, 81, 78, 74, 70],
        C112=[50, 56, 63, 69, 75, 81, 88, 94, 100],
        C212=[100, 99, 98, 96, 95, 94, 93, 91, 90],
        C113=[50, 56, 63, 69, 75, 81, 88, 94, 100],
        C213=[100, 94, 88, 81, 75, 69, 63, 56, 50],
        C114=[100, 96, 93, 89, 85, 81, 78, 74, 70],
        C214=[90, 91, 93, 94, 95, 96, 98, 99, 100],
        C115=[90, 91, 93, 94, 95, 96, 98, 99, 100],
        C215=[100, 94, 88, 81, 75, 69, 63, 56, 50]
    )


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    timeout = models.IntegerField(initial=0)
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    svo = models.FloatField()
    svo_type = models.StringField()

class SVO(Page):
    form_model = 'player'
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6']

    timeout_seconds = 5 * 60

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            **C.svo_values
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        svo_values = C.svo_values

        svo1 = (svo_values['C11'][player.q1 - 1] +
                svo_values['C12'][player.q2 - 1] +
                svo_values['C13'][player.q3 - 1] +
                svo_values['C14'][player.q4 - 1] +
                svo_values['C15'][player.q5 - 1] +
                svo_values['C16'][player.q6 - 1]) / 6 - 50
        svo2 = (svo_values['C21'][player.q1 - 1] +
                svo_values['C22'][player.q2 - 1] +
                svo_values['C23'][player.q3 - 1] +
                svo_values['C24'][player.q4 - 1] +
                svo_values['C25'][player.q5 - 1] +
                svo_values['C26'][player.q6 - 1]) / 6 - 50

        svo3 = svo2 / svo1
        player.participant.svo = svo3

        if svo3 >= 1.5488:
            player.svo = 1
            player.participant.svo_type = 'Altruism'
        if 1.5488 > svo3 >= 0.441:
            player.svo = 2
            player.participant.svo_type = 'Prosocial'
        if 0.441 > svo3 >= -0.213:
            player.participant.svo = 3
            player.svo_type = 'Individualistic'
        if svo3 < -0.213:
            player.svo = 3
            player.participant.svo_type = 'Competitive'

        player.participant.svopayoff = (svo_values['C11'][player.q1 - 1] +
                svo_values['C12'][player.q2 - 1] +
                svo_values['C13'][player.q3 - 1] +
                svo_values['C14'][player.q4 - 1] +
                svo_values['C15'][player.q5 - 1] +
                svo_values['C16'][player.q6 - 1]) / 100

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.dropout == False

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.dropout == False

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

page_sequence = [SVO, Results]
