from NEAT.utils.genotype_class import Genotype
from NEAT.utils.species import Specie
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import numpy as np


def visualize_single(genotype: 'Genotype'):
    # Node visualization
    nodes = {}
    bias_id = None
    for node in genotype.nodes:
        if node.placement != 'Bias':
            nodes.setdefault(node.layer, []).append(node.id)
        else:
            bias_id = node.id
    nodes_coordinates = {}
    max_layer = max(list(nodes.keys()))
    for layer, val in nodes.items():
        num = len(val) + 1
        for i, node in enumerate(val):
            nodes_coordinates[node] = (layer / max_layer, (i + 1) / num)
    X_nodes = []
    Y_nodes = []
    for x, y in nodes_coordinates.values():
        X_nodes.append(x)
        Y_nodes.append(y)

    # Connection visualization
    X_conn_enabled = []
    Y_conn_enabled = []
    X_conn_rec = []
    Y_conn_rec = []
    X_conn_disabled = []
    Y_conn_disabled = []
    e_w = []
    r_w = []
    d_w = []
    for connection in genotype.connections:
        enabled = connection.enabled
        input, output = connection.g_in, connection.g_out
        if input == bias_id or output == bias_id:
            continue
        x_1, y_1 = nodes_coordinates[input]
        x_2, y_2 = nodes_coordinates[output]
        if enabled:
            if connection.is_recurrent:
                X_conn_rec += [x_1, x_2, None]
                Y_conn_rec += [y_1, y_2, None]
                r_w.append(connection.weight)
            else:
                X_conn_enabled += [x_1, x_2, None]
                Y_conn_enabled += [y_1, y_2, None]
                e_w.append(connection.weight)
        else:
            X_conn_disabled += [x_1, x_2, None]
            Y_conn_disabled += [y_1, y_2, None]
            d_w.append(connection.weight)
    x_range = (-0.5, len(nodes) - 0.5)
    return X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range, e_w, r_w, d_w


def visualize(to_plot):
    if isinstance(to_plot, Genotype):
        X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range, e_w, r_w, d_w = visualize_single(
            to_plot)
        plt.scatter(X_nodes, Y_nodes)
        plt.plot(X_conn_enabled, Y_conn_enabled, c='g')
        # plt.plot(X_conn_disabled, Y_conn_disabled, c='r')
        plt.plot(X_conn_rec, Y_conn_rec, c='b')
        for i in range(len(X_conn_enabled) // 3):
            x = (X_conn_enabled[i * 3] + X_conn_enabled[i * 3 + 1]) / 2
            y = (Y_conn_enabled[i * 3] + Y_conn_enabled[i * 3 + 1]) / 2
            plt.text(x, y, str(e_w[i])[:5])
        plt.yticks([])
        plt.xticks([])
        plt.show()
        return None

    # if to_plot is not a single genotype instance, I expect a population i.e. list of genotypes

    if isinstance(to_plot, list) and all(isinstance(x, Genotype) for x in to_plot):
        # first view
        index = 0
        X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range, e_w, r_w, d_w = visualize_single(
            to_plot[index])
        enabled_line, = plt.plot(X_conn_enabled, Y_conn_enabled, c='g')
        disabled_line, = plt.plot(X_conn_disabled, Y_conn_disabled, c='r')
        rec_line, = plt.plot(X_conn_rec, Y_conn_rec, c='b')
        nodes, = plt.plot(X_nodes, Y_nodes, 'o', picker=True, c='b', pickradius=5)

        annotations = [plt.text(0, 0, '') for _ in range(1000)]
        for i in range(len(X_conn_enabled) // 3):
            x = (X_conn_enabled[i * 3] + X_conn_enabled[i * 3 + 1]) / 2
            y = (Y_conn_enabled[i * 3] + Y_conn_enabled[i * 3 + 1]) / 2
            annotations[i].set(text=str(e_w[i])[:5],
                               x=x,
                               y=y)

        # setting plot parameters
        plt.yticks([])
        plt.xticks([])
        plt.subplots_adjust(left=0.25, bottom=0.20)

        ax_individual = plt.axes([0.25, 0.10, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        rax = plt.axes([0.025, 0.73, 0.15, 0.15], facecolor='lightgoldenrodyellow')
        resetax = plt.axes([0.8, 0.025, 0.1, 0.04])

        disabled_line.set_visible(not disabled_line.get_visible())

        individual = Slider(ax=ax_individual,
                            label='Individual',
                            valmin=0,
                            valmax=len(to_plot) - 1,
                            valinit=0,
                            valstep=1)

        check = CheckButtons(rax, ('enabled', 'disabled', 'recurrent'), (True, False, True))
        c = ['g', 'r', 'b']
        [rec.set_facecolor(c[i]) for i, rec in enumerate(check.rectangles)]

        button = Button(resetax, 'Reset', color='lightgoldenrodyellow', hovercolor='0.975')

        # plot events
        def update(val):

            index = individual.val
            X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range, e_w, r_w, d_w = visualize_single(
                to_plot[index])
            enabled_line.set_xdata(X_conn_enabled)
            enabled_line.set_ydata(Y_conn_enabled)
            disabled_line.set_xdata(X_conn_disabled)
            disabled_line.set_ydata(Y_conn_disabled)
            nodes.set_xdata(X_nodes)
            nodes.set_ydata(Y_nodes)
            rec_line.set_xdata(X_conn_rec)
            rec_line.set_ydata(Y_conn_rec)
            for ann in annotations:
                ann.set(text='')
            for i in range(len(X_conn_enabled) // 3):
                x = (X_conn_enabled[i * 3] + X_conn_enabled[i * 3 + 1]) / 2
                y = (Y_conn_enabled[i * 3] + Y_conn_enabled[i * 3 + 1]) / 2
                annotations[i].set(text=str(e_w[i])[:5],
                                   x=x,
                                   y=y)

        def func(label):
            if label == 'enabled':
                enabled_line.set_visible(not enabled_line.get_visible())
            elif label == 'disabled':
                disabled_line.set_visible(not disabled_line.get_visible())
            elif label == 'recurrent':
                rec_line.set_visible(not rec_line.get_visible())
            plt.draw()

        def reset(event):
            individual.reset()

        text = "Species:\n0: " + str(len(to_plot))

        plt.figtext(.02, .4, text)

        button.on_clicked(reset)
        check.on_clicked(func)
        individual.on_changed(update)
        plt.show()

    if isinstance(to_plot, list) and all(isinstance(x, Specie) for x in to_plot):
        if len(to_plot) == 1:
            visualize(to_plot[0].members)
            return None
        # first view
        index = 0
        specie_index = 0
        X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range, e_w, r_w, d_w = visualize_single(
            to_plot[specie_index].members[index])
        enabled_line, = plt.plot(X_conn_enabled, Y_conn_enabled, c='g')
        disabled_line, = plt.plot(X_conn_disabled, Y_conn_disabled, c='r')
        rec_line, = plt.plot(X_conn_rec, Y_conn_rec, c='b')
        nodes, = plt.plot(X_nodes, Y_nodes, 'o', picker=True, c='b', pickradius=5)

        annotations = [plt.text(0, 0, '') for _ in range(1000)]
        for i in range(len(X_conn_enabled) // 3):
            x = (X_conn_enabled[i * 3] + X_conn_enabled[i * 3 + 1]) / 2
            y = (Y_conn_enabled[i * 3] + Y_conn_enabled[i * 3 + 1]) / 2
            annotations[i].set(text=str(e_w[i])[:5],
                               x=x,
                               y=y)

        # setting plot parameters
        plt.yticks([])
        plt.xticks([])
        plt.subplots_adjust(left=0.25, bottom=0.20)

        ax_individual = plt.axes([0.25, 0.13, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        ax_specie = plt.axes([0.25, 0.07, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        rax = plt.axes([0.025, 0.73, 0.15, 0.15], facecolor='lightgoldenrodyellow')

        disabled_line.set_visible(not disabled_line.get_visible())

        individual = Slider(ax=ax_individual,
                            label='Individual',
                            valmin=0,
                            valmax=max([len(specie.members) for specie in to_plot]) - 1,
                            valinit=0,
                            valstep=1)

        specie_slider = Slider(ax=ax_specie,
                               label='Specie',
                               valmin=0,
                               valmax=len(to_plot) - 1,
                               valinit=0,
                               valstep=1)

        check = CheckButtons(rax, ('enabled', 'disabled', 'recurrent'), (True, False, True))
        c = ['g', 'r', 'b']
        [rec.set_facecolor(c[i]) for i, rec in enumerate(check.rectangles)]

        # plot events
        def update(val):
            specie_index = specie_slider.val
            individual.valmax = len(to_plot[specie_index].members) - 1
            index = individual.val
            if index >= len(to_plot[specie_index].members):
                individual.val = 0
                individual.valinit = 0
                index = 0
            X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range, e_w, r_w, d_w = visualize_single(
                to_plot[specie_index].members[index])
            enabled_line.set_xdata(X_conn_enabled)
            enabled_line.set_ydata(Y_conn_enabled)
            disabled_line.set_xdata(X_conn_disabled)
            disabled_line.set_ydata(Y_conn_disabled)
            nodes.set_xdata(X_nodes)
            nodes.set_ydata(Y_nodes)
            rec_line.set_xdata(X_conn_rec)
            rec_line.set_ydata(Y_conn_rec)

            for ann in annotations:
                ann.set(text='')
            for i in range(len(X_conn_enabled) // 3):
                x = (X_conn_enabled[i * 3] + X_conn_enabled[i * 3 + 1]) / 2
                y = (Y_conn_enabled[i * 3] + Y_conn_enabled[i * 3 + 1]) / 2
                annotations[i].set(text=str(e_w[i])[:5],
                                   x=x,
                                   y=y)

        def func(label):
            if label == 'enabled':
                enabled_line.set_visible(not enabled_line.get_visible())
            elif label == 'disabled':
                disabled_line.set_visible(not disabled_line.get_visible())
            elif label == 'recurrent':
                rec_line.set_visible(not rec_line.get_visible())
            plt.draw()

        text = "Best score:\n"
        text += str(max([max(specie.fitness) for specie in to_plot]))
        text += '\nSpecies:\n'
        text += ''.join([str(i) + ': ' + str(len(specie.members)) + '\n' for i, specie in enumerate(to_plot[:7])])

        plt.figtext(.02, .34, text)

        check.on_clicked(func)
        individual.on_changed(update)
        specie_slider.on_changed(update)
        plt.show()
