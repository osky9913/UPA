from mongo.queryA import plot_queries_A_boxplot, plot_queries_A_vaccinations_1, plot_queries_A_vaccinations_2, plot_queries_A_vaccinations_3, plot_queries_comparision


def main():
    print("Plotting graphs from section A")
    plot_queries_A_boxplot()
    plot_queries_A_vaccinations_1()
    plot_queries_A_vaccinations_2()
    plot_queries_A_vaccinations_3()

    print("Plotting comparision diagram")
    plot_queries_comparision()


if __name__ == "__main__":
    main()
