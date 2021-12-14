import pygame
import pygame.draw
import platform

from sitnikov_gui import init_ui
from sitnikov_theory import Theory
from sitnikov_model import State, Sitnikov


# displaying the actual size of the window, Windows only
if platform.system() == 'Windows':
    import ctypes

    ctypes.windll.user32.SetProcessDPIAware()

pygame.init()

surface = pygame.display.set_mode((1700, 800))
clock = pygame.time.Clock()

STATE = State()
SITNIKOV = Sitnikov(STATE, surface)

# Initialise the UI

UI = init_ui(surface, STATE)
Theory = Theory(SITNIKOV)

UI.add_hotkey(pygame.K_g, SITNIKOV.show_plots, [STATE])
UI.add_hotkey(pygame.K_s, STATE.switch_stats)

UI.add_button('open_docs', loc=(50, SITNIKOV.height - 50 - 64), size=(64, 64), image_path='open_docs_icon.png')
UI.add_button('theor_model', loc=(75 + 64, SITNIKOV.height - 50 - 64), size=(64, 64), image_path='open_th_graphs_icon.png')
UI.add_button('num_graph', loc=(100 + 2 * 64, SITNIKOV.height - 50 - 64), size=(64, 64), image_path='open_num_graphs_icon.png')

UI['open_docs'].connect(SITNIKOV.open_documentation)
UI['theor_model'].connect(Theory.plot_theory)
UI['num_graph'].connect(SITNIKOV.show_plots, [STATE])


while True:
    for event in pygame.event.get():
        UI = SITNIKOV.event_tracking(event, UI)

    clock.tick(STATE.fps)
    SITNIKOV.frame_rendering()

    if STATE.statistics:
        SITNIKOV.display_stats()

    UI.update()

    pygame.display.flip()

