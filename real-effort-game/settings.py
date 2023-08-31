from os import environ


SESSION_CONFIGS = [
    dict(
        name='slider',
        display_name='Slider Task',
        app_sequence=['intro', 'slider_bench', 'slider_2', 'svo', 'results'],
        num_demo_participants=8,
        ret_slider_num=90,
        ret_slider_ncols=1,
        bonus_per_slider=5
    ),
]

ROOMS = [
    dict(
        name='virtual_lab',
        display_name='Virtual Lab',
        participant_label_file='_rooms/virtual_lab.txt'
    )
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.05, participation_fee=0.20, doc="",
    mturk_hit_settings=dict(
    keywords='bonus, study',
    title='Multiplayer Real Effort Game',
    description='This HIT is a multiple-person task. You earn money by completing 2 rounds of simple slider tasks and coordinating with your teammates. It is a multiplayer game so we respectfully ask you to follow the instructions carefully and stay engaged throughout the experiment.',
    frame_height = 500,
    template = 'global/mturk_template.html',
    minutes_allotted_per_assignment = 60,
    expiration_hours = 7 * 24,
    qualification_requirements=[
        {
            'QualificationTypeId': "3KNFVBDQIWM1X8ICITGYFQEBWZE03Y",
            'Comparator': "DoesNotExist",
        },
    ],
    grant_qualification_id = '3KNFVBDQIWM1X8ICITGYFQEBWZE03Y', # to prevent retakes
)
)

PARTICIPANT_FIELDS = [
    'round1_payoff',
    'round2_payoff',
    'total_payoff',
    'lottery',
    'par_payoff',
    'payoff_real',
    'dropout',
    'excluded',
    'svo',
    'svo_type',
    'svopayoff',
    'finished'
]

SESSION_FIELDS = ['round_to_pay', 'prolific_completion_url']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'token'

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '4221376580418'
