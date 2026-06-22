from micron_per import get_micron_data
from samsung_per import get_samsung_data
from skhynix_per import get_skhynix_data
from analysis import make_analysis


def run():
    raw_data = [
        get_micron_data(),
        get_samsung_data(),
        get_skhynix_data()
    ]

    results = [make_analysis(d) for d in raw_data]

    print("\n=== Semiconductor Analysis ===\n")

    for r in results:
        print(f"{r['name']}")
        print(f"Price: {r['price']}")
        print(f"EPS: {r['eps']}")
        print(f"PER: {r['pe']}")
        print(f"Fair Value: {r['fair_value']}")
        print(f"Gap: {r['gap']}")
        print("-----------------------")


if __name__ == "__main__":
    run()