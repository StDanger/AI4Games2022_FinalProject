from NEAT.utils.genotype_class import Genotype
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons


def visualize_single(genotype: Genotype, plot_disabled):
    # Node visualization
    nodes = {}
    for node in genotype.nodes:
        nodes.setdefault(node.layer, []).append(node.id)

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
    for connection in genotype.connections:
        enabled = connection.enabled
        if plot_disabled or enabled:
            input, output = connection.g_in, connection.g_out
            x_1, y_1 = nodes_coordinates[input]
            x_2, y_2 = nodes_coordinates[output]
            if enabled:
                if connection.is_recurrent:
                    X_conn_rec += [x_1, x_2, None]
                    Y_conn_rec += [y_1, y_2, None]
                else:
                    X_conn_enabled += [x_1, x_2, None]
                    Y_conn_enabled += [y_1, y_2, None]
            else:
                X_conn_disabled += [x_1, x_2, None]
                Y_conn_disabled += [y_1, y_2, None]
    x_range = (-0.5, len(nodes) - 0.5)
    return X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range


def visualize(to_plot, plot_disabled=False):
    if isinstance(to_plot, Genotype):
        X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range = visualize_single(
            to_plot, plot_disabled=plot_disabled)
        plt.scatter(X_nodes, Y_nodes)
        plt.plot(X_conn_enabled, Y_conn_enabled, c='g')
        plt.plot(X_conn_disabled, Y_conn_disabled, c='r')
        plt.plot(X_conn_rec, Y_conn_rec, c='b')
        plt.yticks([])
        plt.xticks([])
        plt.show()
        return None

    # if to_plot is not a single genotype instance, I expect a population i.e. list of genotypes

    # first view
    index = 0
    X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range = visualize_single(
        to_plot[index], plot_disabled=plot_disabled)
    enabled_line, = plt.plot(X_conn_enabled, Y_conn_enabled, c='g')
    disabled_line, = plt.plot(X_conn_disabled, Y_conn_disabled, c='r')
    rec_line, = plt.plot(X_conn_rec, Y_conn_rec, c='b')
    nodes, = plt.plot(X_nodes, Y_nodes, 'o', picker=True, c='b', pickradius=5)

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
        X_conn_rec, Y_conn_rec, X_nodes, Y_nodes, X_conn_enabled, Y_conn_enabled, X_conn_disabled, Y_conn_disabled, x_range = visualize_single(
            to_plot[index], plot_disabled=plot_disabled)
        enabled_line.set_xdata(X_conn_enabled)
        enabled_line.set_ydata(Y_conn_enabled)
        disabled_line.set_xdata(X_conn_disabled)
        disabled_line.set_ydata(Y_conn_disabled)
        nodes.set_xdata(X_nodes)
        nodes.set_ydata(Y_nodes)
        rec_line.set_xdata(X_conn_rec)
        rec_line.set_ydata(Y_conn_rec)

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

    plt.figtext(.02, .4, 'There is an option\nto add a side info:\n'+'- a\n'*5)

    button.on_clicked(reset)
    check.on_clicked(func)
    individual.on_changed(update)
    plt.show()
