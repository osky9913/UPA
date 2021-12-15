from mongo.queryA import plot_queries_A_boxplot, plot_queries_A_vaccinations_1, plot_queries_A_vaccinations_2, plot_queries_A_vaccinations_3, plot_queries_comparision
from mongo.queryB import plot_queries_B_ranking


def main():
    print("Plotting graphs from section A")
    plot_queries_A_boxplot()
    plot_queries_A_vaccinations_1()
    plot_queries_A_vaccinations_2()
    plot_queries_A_vaccinations_3()
    plot_queries_comparision()
    print("Plotting graphs from section B")
    plot_queries_B_ranking()


if __name__ == "__main__":
    main()
