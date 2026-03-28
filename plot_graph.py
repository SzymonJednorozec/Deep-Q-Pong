import matplotlib.pyplot as plt
from IPython import display


plt.ion()

def plot(scores, mean_scores,epsilons):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.plot(epsilons)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.text(len(epsilons)-1, epsilons[-1], str(epsilons[-1]))
    plt.show(block=False)
    plt.pause(.1)


def generate_and_save_plots(plot_data_list, epsilons, save_path="model/training_plot.png"):
    num_instances = len(plot_data_list)
    
    fig, axes = plt.subplots(num_instances + 1, 1, figsize=(10, 4 * (num_instances + 1)))

    for i, info in enumerate(plot_data_list):
        ax = axes[i]
        ax.set_title(f'Instance {i+1} Training')
        ax.set_ylabel('Score')
        ax.plot(info.scores, label='Score', color='blue')
        ax.plot(info.mean_scores, label='Mean Score', color='orange')
        ax.legend()

        if info.scores:
            ax.text(len(info.scores)-1, info.scores[-1], str(info.scores[-1]))
            ax.text(len(info.mean_scores)-1, info.mean_scores[-1], f"{info.mean_scores[-1]:.2f}")

    ax_eps = axes[-1]
    ax_eps.set_title('Global Epsilon Decay')
    ax_eps.set_xlabel('Total Games Finished (Across all instances)')
    ax_eps.set_ylabel('Epsilon')
    ax_eps.plot(epsilons, color='red')
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig) 