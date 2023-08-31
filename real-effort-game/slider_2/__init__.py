from otree.api import *

c = Currency

doc = """
Real effort task, based on moving sliders, as in:
Gill, David, and Victoria Prowse. 2012.
"A Structural Analysis of Disappointment Aversion in a Real Effort Competition."
American Economic Review, 102 (1): 469-503.
DOI: 10.1257/aer.102.1.469
"""


class C(BaseConstants):
    NAME_IN_URL = 'slider_2'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 1

    # Set task parameters
    sliders_task_pms = dict(
        time_in_seconds = 30, # slider timer
        num = 48,
        ncols = 1,
        max = 100,
        min = 0,
        target = 50,
        bonus_per_slider = 5,
        default = 'min',          # Sliders default value when the task begin
        num_centered = 0,
        bonus = cu(0)
    )

    # pre_ret: introduction timer; start_next_part: intersection timer
    timers = dict(pre_ret = 120, start_next_part = 120)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = models.IntegerField() # treatments
    has_dropout = models.BooleanField(initial=False)


class Player(BasePlayer):
    # do roles
    def role(self):
        if self.id_in_group <= 2:
            return 'A'
        else:
            return 'B'

    timeout = models.IntegerField(initial=0)
    num_centered = models.IntegerField()
    bonus_per_slider = models.FloatField()
    excluded = models.BooleanField(initial=False)
    # Whether the player chooses to contribute
    cooperate = models.BooleanField(label = "Would you agree to change the system to upward-sloping?",
                                    choices = [
                                        [False, "Stay in Current System"],
                                        [True, "Agree to Change System"]
                                    ])

# FUNCTIONS
def creating_session(subsession: Subsession):
    import random
    for group in subsession.get_groups():
        for p in group.get_players():
            p.participant.round1_payoff = 0
            p.participant.round2_payoff = 0
            p.participant.total_payoff = 0
            p.participant.svopayoff = 0
            if p.participant.dropout == True:
                group.has_dropout = True

    if subsession.round_number == 1:
        session = subsession.session
        config = session.config
        const = C
        sliders_task_pms = const.sliders_task_pms.copy()
        if 'ret_slider_num' in config:
            sliders_task_pms.update(
                num = config['ret_slider_num'],
                ncols = config['ret_slider_ncols']
            )
        session.vars['sliders_task_pms'] = sliders_task_pms

# set drop out WILL NEED TO CHANGE
def set_dropout(player: Player, num_centered: int):
    if num_centered <= 0:

        player.participant.dropout = True
        player.group.has_dropout = True


def set_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def set_sliders_task(player: Player, const: C):
    # Import module needed
    from random import randint, choice

    # Copy task parameters from session
    session = player.session
    if not 'low' in player.session.vars:
        player.session.vars['low'] = True # If not set yet, set system type to low

    task = player.session.vars['sliders_task_pms'].copy()

    # Set random value for left margin of sliders in each row
    offsets = [randint(0, 10) for _ in range(task['num'] // task['ncols'])]

    # Set default values of sliders: either to "min" or to random values
    if task['default'] == 'min':
        m = task['min']
        curr_values = [m for _ in range(task['num'])]
    else:
        input_range = list(range(task['min'], task['max']))
        input_range.remove(task['target'])
        curr_values = [choice(input_range) for _ in range(task['num'])]

    # Set list of rows containing the sliders: each row contains 3 sliders and the left margin for that row
    sliders = list(zip(set_chunks(curr_values, task['ncols']), offsets))

    # Flag task as set
    sliders_task_set = True

    # Update dictionary containing task parameters
    task.update(offsets=offsets, curr_values=curr_values, sliders=sliders)

    return sliders_task_set, task


# PAGES
class StartWaitPage(WaitPage):
    group_by_arrival_time = True

    @staticmethod
    def is_displayed(player):
        return player.participant.dropout == False

    @staticmethod
    def after_all_players_arrive(group: Group):
        import random
        group.treatment = random.randint(0, 2)

class IntroA(Page):
    timeout_seconds = C.timers['pre_ret']

    @staticmethod
    def is_displayed(player):
        return player.role() == "A" and player.group.has_dropout == False

    @staticmethod
    def vars_for_template(player: Player):
        lottery0 = " "
        lottery1 = " "
        lottery2 = " "
        if player.group.treatment == 1:
            lottery0 = " COMPETITION SYSTEM "
            lottery1 = "The game has a competition system. If, after all players complete the two rounds, your total WAGE ranks 1st among your opponents, you gain 7 tokens as an EXTRA reward."
            lottery2 = "If there is a tie, computer will randomize a winner. There will only be ONE winner in the group. "

        treatment1 = "  "
        if player.group.treatment != 0:
            treatment1 = "There are THREE rounds of tasks. You are the randomized as A, which means you complete rounds 1 and 2. Players randomized as B will complete rounds 2 and 3."

        return {
            "treatment1": treatment1,
            "lottery0": lottery0,
            "lottery1": lottery1,
            "lottery2": lottery2,
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        participant = player.participant
        if timeout_happened:
            group.has_dropout = True

            player.participant.dropout = True

class IntroB(Page):
    timeout_seconds = C.timers['pre_ret']

    @staticmethod
    def is_displayed(player):
        return player.role() == "B" and player.group.has_dropout == False

    @staticmethod
    def vars_for_template(player: Player):
        lottery0 = " "
        lottery1 = " "
        lottery2 = " "
        if player.group.treatment == 1:
            lottery0 = " COMPETITION SYSTEM "
            lottery1 = "The game has a competition system. If, after all players complete the two rounds, your total WAGE ranks 1st among your opponents, you gain 7 tokens as an EXTRA reward."
            lottery2 = "If there is a tie, computer will randomize a winner. There will only be ONE winner in the group. "
        treatment2 = " "
        if player.group.treatment != 0:
            treatment2 = "There are THREE rounds of tasks. You are the randomized as B, which means you complete rounds 2 and 3. Players randomized as A will complete rounds 1 and 2."

        return {
            "lottery1": lottery1,
            "lottery2": lottery2,
            "lottery0": lottery0,
            "treatment2": treatment2
        }
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        participant = player.participant
        if timeout_happened:
            group.has_dropout = True
            player.participant.dropout = True

class A1Page(Page):

    @staticmethod
    def is_displayed(player):
        return player.role() == "A" and player.group.has_dropout == False

    timeout_seconds = C.sliders_task_pms['time_in_seconds']
    timer_text = 'Time Remaining: '

    @staticmethod
    def vars_for_template(player: Player):
        pvars = player.participant.vars
        # set a new task
        pvars['sliders_task_set'], pvars['sliders_task'] = set_sliders_task(player, C)

        # Returns the dictionary containing the task parameters as variables for the template
        return pvars['sliders_task']

    @staticmethod
    def live_method(player: Player, data):
        sliders_task_pms = player.session.vars['sliders_task_pms']
        participant = player.participant
        # Get task parameters
        task = participant.vars['sliders_task']

        # Get updated number of centered sliders
        num_centered = len([v for v in data if v == task['target']])

        # Update task parameters based on: current values of the sliders, number of centered sliders, bonus accumulated
        task.update(
            sliders = list(zip(set_chunks(data, task['ncols']), task['offsets'])),
            num_centered = num_centered,
            bonus = round((5 * (1 - 0.9 ** num_centered))/0.1, 2), # update bonus
            bonus_per_slider = round(5 * (0.9 ** (num_centered - 1)), 2), # per-slider wage update
            finished = num_centered == sliders_task_pms['num'], # If all sliders are centered or timeout happened then finished = true
        )
        player.participant.round1_payoff = task['bonus']

        # Send updated task's parameters to the webpage
        return {player.id_in_group: dict(num_centered = num_centered, bonus_per_slider = task['bonus_per_slider'], bonus = task['bonus'], finished = task['finished'])}

    # Set player fields with number of centered sliders and payoff
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        task = participant.vars['sliders_task']
        player.num_centered = task['num_centered']
        player.bonus_per_slider = task['bonus_per_slider']
        #set_dropout(player, task['num_centered'])

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class CoordinationA(Page):

    @staticmethod
    def is_displayed(player):
        return player.role() == "A" and player.group.treatment != 0 and player.group.has_dropout == False

    timeout_seconds = C.timers['start_next_part']
    timer_text = 'Time Remaining: '

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True
            player.group.has_dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

    @staticmethod
    def vars_for_template(player: Player):
        lottery = "Please read the following VERY CAREFULLY: "
        if player.group.treatment == 1:
            lottery = "Recall the COMPETITION SYSTEM. If, after all players complete the two rounds, your TOTAL WAGE ranks 1st among your opponents, you gain an extra 7 tokens as a reward."
        return {
            "lottery": lottery
        }

    form_model = "player"
    form_fields = ["cooperate"]

class CoordinationA1(Page):

    @staticmethod
    def is_displayed(player):
        return player.role() == "A" and player.group.treatment == 0 and player.group.has_dropout == False

    timeout_seconds = C.timers['start_next_part']
    timer_text = 'Time Remaining: '

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True
            player.group.has_dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

    form_model = "player"
    form_fields = ["cooperate"]

class CoordinationB(Page):

    @staticmethod
    def is_displayed(player):
        return player.role() == "B" and player.group.treatment != 0 and player.group.has_dropout == False

    timeout_seconds = C.timers['start_next_part']
    timer_text = 'Time Remaining: '

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True
            player.group.has_dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

    form_model = "player"
    form_fields = ["cooperate"]

class CoordinationB1(Page):

    @staticmethod
    def is_displayed(player):
        return player.role() == "B" and player.group.treatment == 0 and player.group.has_dropout == False

    timeout_seconds = C.timers['start_next_part']
    timer_text = 'Time Remaining: '

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True
            player.group.has_dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

    form_model = "player"
    form_fields = ["cooperate"]

class CoordinationResult(Page):
    timeout_seconds = C.timers['start_next_part']
    timer_text = 'Time Remaining: '

    @staticmethod
    def vars_for_template(player: Player):
        decision = " Change to Upward-sloping System. " if player.cooperate else " Stay in Current System. "
        return {
            "decision": decision
        }

    @staticmethod
    def is_displayed(player):
        return player.group.has_dropout == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True
            player.group.has_dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class ResultWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.group.has_dropout == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class transitionPage(Page):
    timeout_seconds = C.timers['pre_ret']
    @staticmethod
    def is_displayed(player):
        return player.group.has_dropout == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

    @staticmethod
    def vars_for_template(player: Player):
        coord = " remains downward sloping because at least one of your group member disagreed to the change. " if player.session.vars["low"] else " has changed to upward-sloping system. Coordination succeeded. "
        return {
            "coord": coord
        }

class A2Page(Page):
    @staticmethod
    def is_displayed(player):
        return player.role() == "A" and player.group.has_dropout == False

    timeout_seconds = C.sliders_task_pms['time_in_seconds']
    timer_text = 'Time Remaining: '

    @staticmethod
    def vars_for_template(player: Player):
        pvars = player.participant.vars
        # If no task exists yet, set a new task
        if not pvars.get('sliders_task_set'):
            pvars['sliders_task_set'], pvars['sliders_task'] = set_sliders_task(player, C)

        # Returns the dictionary containing the task parameters as variables for the template
        return pvars['sliders_task']

    @staticmethod
    def live_method(player: Player, data):
        sliders_task_pms = player.session.vars['sliders_task_pms']
        participant = player.participant
        curr_per_slider = player.bonus_per_slider * 0.9 if player.session.vars['low'] else 1.1 * player.bonus_per_slider
        curr_num_centered = player.num_centered

        # Get task parameters
        task = participant.vars['sliders_task']

        # Get updated number of centered sliders
        num_centered = len([v for v in data if v == task['target']])

        # Update task parameters based on: current values of the sliders, number of centered sliders, bonus accumulated
        task.update(
            sliders = list(zip(set_chunks(data, task['ncols']), task['offsets'])),
            num_centered = num_centered,
            bonus = participant.round1_payoff + round((curr_per_slider * (1 - 0.9 ** (num_centered - curr_num_centered)))/0.1, 2) if player.session.vars['low'] else participant.round1_payoff + round((curr_per_slider * (1.1 ** (num_centered - curr_num_centered) - 1))/0.1, 2), # update bonus
            bonus_per_slider = round(curr_per_slider * (0.9 ** ((num_centered - curr_num_centered) - 1)), 2) if player.session.vars['low'] else round(curr_per_slider * (1.1 ** ((num_centered - curr_num_centered) - 1)), 2), # per-slider wage update
            finished = num_centered == sliders_task_pms['num'], # If all sliders are centered or timeout happened then finished = true
        )

        player.participant.round2_payoff = task['bonus'] - player.participant.round1_payoff

        # Send updated task's parameters to the webpage
        return {player.id_in_group: dict(num_centered = num_centered, bonus = task['bonus'], finished = task['finished'])}

    # Set player fields with number of centered sliders and payoff
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        task = participant.vars['sliders_task']
        player.num_centered = task['num_centered']

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class B1Page(Page):
    @staticmethod
    def is_displayed(player):
        return player.role() == "B" and player.group.has_dropout == False

    timeout_seconds = C.sliders_task_pms['time_in_seconds']
    timer_text = 'Time Remaining: '

    @staticmethod
    def vars_for_template(player: Player):
        pvars = player.participant.vars
        # set a new task
        pvars['sliders_task_set'], pvars['sliders_task'] = set_sliders_task(player, C)

        # Returns the dictionary containing the task parameters as variables for the template
        return pvars['sliders_task']

    @staticmethod
    def live_method(player: Player, data):
        sliders_task_pms = player.session.vars['sliders_task_pms']
        participant = player.participant

        # Get task parameters
        task = participant.vars['sliders_task']

        # Get updated number of centered sliders
        num_centered = len([v for v in data if v == task['target']])

        # Update task parameters based on: current values of the sliders, number of centered sliders, bonus accumulated
        task.update(
            sliders=list(zip(set_chunks(data, task['ncols']), task['offsets'])),
            num_centered=num_centered,
            bonus = round((5 * (1 - 0.9 ** num_centered))/0.1, 2) if player.session.vars['low'] else round((5 * (1.1 ** num_centered - 1))/0.1, 2), # update bonus
            bonus_per_slider = round(5 * (0.9 ** (num_centered - 1)), 2) if player.session.vars['low'] else round(5 * (1.1 ** (num_centered - 1)), 2), # per-slider wage update
            finished = num_centered == sliders_task_pms['num']
        )

        player.participant.round1_payoff = task['bonus']

        # Send updated task's parameters to the webpage
        return {player.id_in_group: dict(num_centered=num_centered, bonus=task['bonus'], finished=task['finished'])}

    # Set player fields with number of centered sliders and payoff
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        task = participant.vars['sliders_task']
        player.num_centered = task['num_centered']
        player.bonus_per_slider = task['bonus_per_slider']
        #set_dropout(player, task['num_centered'])

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class BtransitionPage(Page):
    timeout_seconds = C.timers['pre_ret']

    @staticmethod
    def is_displayed(player):
        return player.role() == "B" and player.group.has_dropout == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:

            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class B2Page(Page):
    @staticmethod
    def is_displayed(player):
        return player.role() == "B" and player.group.has_dropout == False

    timeout_seconds = C.sliders_task_pms['time_in_seconds']
    timer_text = 'Time Remaining: '

    @staticmethod
    def vars_for_template(player: Player):
        pvars = player.participant.vars
        # If no task exists yet, set a new task
        if not pvars.get('sliders_task_set'):
            pvars['sliders_task_set'], pvars['sliders_task'] = set_sliders_task(player, C)

        # Returns the dictionary containing the task parameters as variables for the template
        return pvars['sliders_task']

    @staticmethod
    def live_method(player: Player, data):
        sliders_task_pms = player.session.vars['sliders_task_pms']
        participant = player.participant
        curr_per_slider = player.bonus_per_slider * 0.9 if player.session.vars['low'] else 1.1 * player.bonus_per_slider
        curr_num_centered = player.num_centered

        # Get task parameters
        task = participant.vars['sliders_task']

        # Get updated number of centered sliders
        num_centered = len([v for v in data if v == task['target']])

        # Update task parameters based on: current values of the sliders, number of centered sliders, bonus accumulated
        task.update(
            sliders=list(zip(set_chunks(data, task['ncols']), task['offsets'])),
            num_centered=num_centered,
            bonus = participant.round1_payoff + round((curr_per_slider * (1 - 0.9 ** (num_centered - curr_num_centered)))/0.1, 2) if player.session.vars['low'] else participant.round1_payoff + round((curr_per_slider * (1.1 ** (num_centered - curr_num_centered) - 1))/0.1, 2), # update bonus
            bonus_per_slider = round(curr_per_slider * (0.9 ** ((num_centered - curr_num_centered) - 1)), 2) if player.session.vars['low'] else round(curr_per_slider * (1.1 ** ((num_centered - curr_num_centered) - 1)), 2), # per-slider wage update
            finished = num_centered == sliders_task_pms['num']
        )

        player.participant.round2_payoff = task['bonus'] - player.participant.round1_payoff

        # Send updated task's parameters to the webpage
        return {player.id_in_group: dict(num_centered=num_centered, bonus=task['bonus'], finished=task['finished'])}

    # Set player fields with number of centered sliders and payoff
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant
        task = participant.vars['sliders_task']
        player.num_centered = task['num_centered']
        #set_dropout(player, task['num_centered'])

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class finalWaitPage(WaitPage):
    timeout_seconds = C.timers['start_next_part']
    timer_text = 'Time Remaining: '

    @staticmethod
    def is_displayed(player):
        return player.group.has_dropout == False

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

    @staticmethod
    def after_all_players_arrive(group: Group):
        players = group.get_players()
        payoff_list = {}
        for p in players:
            p.participant.total_payoff = p.participant.round1_payoff + p.participant.round2_payoff # calculate player's total payoff
            payoff_list[p.id_in_group] = p.participant.total_payoff # add to payoff list

        payoff_list = dict(sorted(payoff_list.items(), key = lambda item: item[1]))
        if group.treatment == 1:
            group.session.vars['winner'] = list(payoff_list)[-1]
        else:
            group.session.vars['winner'] = 100
        for p in players:
            if p.id_in_group == p.session.vars['winner']:
                p.participant.total_payoff += 7

        for p in players:
            p.participant.round1_payoff = round(p.participant.round1_payoff)
            p.participant.round2_payoff = round(p.participant.round2_payoff)
            p.participant.total_payoff = round(p.participant.total_payoff)

class Results(Page):
    timeout_seconds = C.timers['start_next_part']
    timer_text = 'Time Remaining: '

    @staticmethod
    def is_displayed(player):
        return player.group.has_dropout == False

    @staticmethod
    def vars_for_template(player: Player):
        winner = " "
        if player.group.treatment == 1:
            winner = "The winner is player " + str(player.session.vars['winner'])
        return {
            "winner": winner
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant.dropout = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        participant = player.participant
        if participant.dropout:
            return upcoming_apps[-1]

class DropoutHappened(Page):
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return group.has_dropout

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        for p in group.get_players():
            if p.participant.dropout == False:
                p.participant.excluded = True

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return upcoming_apps[-1]

page_sequence = [StartWaitPage,
                 IntroA,
                 IntroB,
                 A1Page,
                 CoordinationB,
                 CoordinationB1,
                 CoordinationA,
                 CoordinationA1,
                 CoordinationResult,
                 ResultWaitPage,
                 transitionPage,
                 A2Page,
                 B1Page,
                 BtransitionPage,
                 B2Page,
                 finalWaitPage,
                 Results,
                 DropoutHappened
                 ]
