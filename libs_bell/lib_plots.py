import matplotlib.pyplot as plt

def plot_correlations_dots(max_size,
                           c_bounds,
                           q_bounds,
                           corrs_list, 
                           stddevs_list,
                           labels,
                           markers,
                           title):
    plt.clf()
    plt.style.use('ggplot')
    plt.plot(list(range(1, max_size + 1)), c_bounds[:max_size], label="Classical bounds") # , marker="o", markersize=3)
    plt.plot(list(range(1, max_size + 1)), q_bounds[:max_size], label="Quantum bounds") # , marker="x", markersize=3)
    for i in range(len(corrs_list)):
        plt.fill_between(list(range(1, len(corrs_list[i]) + 1)),
                         corrs_list[i] - stddevs_list[i], corrs_list[i] + stddevs_list[i], alpha=0.2)
        plt.errorbar(list(range(1, len(corrs_list[i]) + 1)),
                     corrs_list[i], label=labels[i], fmt=markers[i], yerr=stddevs_list[i], capsize=3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.xlabel("graph size")
    plt.ylabel("correlation value")
    plt.xticks(list(range(max_size + 2))[::2])
    plt.title(title)
    plt.show()

def cut_corrs_list(corrs_list, max_size):
    new_corrs_list = []
    for corr_list in corrs_list:
        new_corrs_list.append( corr_list[:max_size] )
    return new_corrs_list


def plot_correlations_lines(max_size,
                            c_bounds,
                            q_bounds,
                            corrs_list,
                            stddevs_list,
                            labels,
                            title):

    plt.clf()
    plt.style.use('ggplot')
    plt.plot(list(range(1, max_size + 1)),
             c_bounds[:max_size], label="Classical bounds")
    plt.plot(list(range(1, max_size + 1)),
             q_bounds[:max_size], label="Quantum bounds")
    for i in range(len(corrs_list)):
        plt.fill_between(list(range(1, len(corrs_list[i]) + 1)), corrs_list[i] - stddevs_list[i], corrs_list[i] + stddevs_list[i], alpha=0.2)
        plt.plot(list(range(1, len(corrs_list[i]) + 1)), corrs_list[i], label = labels[i])
        # plt.errorbar(list(range(1, len(corrs_list[i]) + 1)), corrs_list[i], label=labels[i], fmt=markers[i], yerr=stddevs_list[i], capsize=3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.xlabel("graph size")
    plt.ylabel("correlation value")
    plt.xticks(list(range(max_size + 2))[::2])
    plt.title(title)
    plt.show()
