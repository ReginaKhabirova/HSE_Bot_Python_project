def build_graph(x, y):
    plt.title('Траты за неделю')
    plt.xlabel('Дни трат')
    plt.ylabel('Сумма за день')
    plt.bar(x, y)

    plt.savefig('expenses_by_week_plot.png', dpi=300)