from otree.api import *

c = Currency


class C(BaseConstants):
    NAME_IN_URL = 'results'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    CUSTOM_POINTS_NAME = 'Token'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# FUNCTIONS
def set_participant_payoff(participant: Player.participant, exchange_rate: float):
    participant.par_payoff = 0.7
    if participant.total_payoff == None or participant.svopayoff == None:
        participant.total_payoff = 0
        participant.svopayoff = 0
    payoff = participant.total_payoff + participant.svopayoff + participant.par_payoff

    #print(participant.round1_payoff, participant.round2_payoff)
    #print(payoff)
    #print(exchange_rate)
    participant.payoff_real = round(payoff * exchange_rate, 2)
    participant.payoff = participant.payoff_real

# PAGES
class TimeOut(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.dropout


class Excluded(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.excluded

    @staticmethod
    def vars_for_template(player: Player):
        exchange_rate = player.session.config['real_world_currency_per_point']
        participant = player.participant
        set_participant_payoff(participant, exchange_rate)
        return dict()

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        exchange_rate = player.session.config['real_world_currency_per_point']
        participant = player.participant
        set_participant_payoff(participant, exchange_rate)
        payoff = participant.payoff_real
        return{
            "payoff": payoff
        }
    @staticmethod
    def is_displayed(player: Player):
        return player.participant.excluded == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.finished = True

class Redirect(Page):
    pass

page_sequence = [TimeOut,
                 Excluded,
                 Results,
                 Redirect
                 ]
