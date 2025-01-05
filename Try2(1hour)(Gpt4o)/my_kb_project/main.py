import argparse
from simulator import run_simulation

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=100, help="Anzahl der Endlos-Impulse")
    parser.add_argument("--delay", type=float, default=0.2, help="Sekunden zwischen Schritten")
    args = parser.parse_args()

    print(f"Starte Simulation mit {args.steps} Schritten, Delay={args.delay}s")
    run_simulation()  # ggf. anpassen, falls du dynamisch steps/delay übergeben willst.

if __name__ == "__main__":

    main()