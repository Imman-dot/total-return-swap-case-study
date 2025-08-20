#!/usr/bin/env python3
"""
TRS_simulation.py
Compares Direct Share Ownership vs Total Return Swap (TRS) exposure.

Outputs:
- data/trs_results.csv              (table of results)
- images/trs_pnl.png               (Direct vs TRS PnL)
- images/trs_return_on_collateral.png  (% return on collateral for TRS)
"""

import argparse
import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import csv


def simulate_trs(
    notional=1_000_000,
    financing_rate=0.05,  # 5% per year
    period_years=1.0,
    collateral=200_000,   # cash posted against TRS (shows leverage)
    move_start=-0.20,     # -20%
    move_stop=0.21,       # +20% (stop is exclusive)
    move_step=0.05        # 5% increments
):
    moves = np.arange(move_start, move_stop, move_step)  # e.g., -0.20 ... +0.20
    direct_pnl = notional * moves

    # TRS: same economic exposure before fees
    trs_before_fee = direct_pnl.copy()

    # Financing cost is paid regardless of market move
    financing_fee = -(notional * financing_rate * period_years)

    trs_net_pnl = trs_before_fee + financing_fee
    trs_return_on_collateral = trs_net_pnl / collateral

    return {
        "moves": moves,
        "direct_pnl": direct_pnl,
        "trs_before_fee": trs_before_fee,
        "financing_fee_each_row": np.full_like(moves, financing_fee),
        "trs_net_pnl": trs_net_pnl,
        "trs_roc": trs_return_on_collateral,
    }


def ensure_dirs():
    # Create folders if they don't exist
    Path("images").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)


def save_csv(sim, outfile="data/trs_results.csv"):
    with open(outfile, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Market Move (%)",
            "Direct Ownership PnL (£)",
            "TRS PnL before Fee (£)",
            "Financing Fee (£)",
            "TRS Net PnL (£)",
            "TRS % Return on Collateral"
        ])
        for i in range(len(sim["moves"])):
            w.writerow([
                round(sim["moves"][i]*100, 1),
                round(float(sim["direct_pnl"][i]), 2),
                round(float(sim["trs_before_fee"][i]), 2),
                round(float(sim["financing_fee_each_row"][i]), 2),
                round(float(sim["trs_net_pnl"][i]), 2),
                round(float(sim["trs_roc"][i]), 4)
            ])


def plot_pnl(sim, outfile="images/trs_pnl.png"):
    x = sim["moves"] * 100  # percentage for x-axis
    plt.figure()
    plt.plot(x, sim["direct_pnl"], label="Direct Ownership PnL")
    plt.plot(x, sim["trs_net_pnl"], label="TRS Net PnL")
    plt.xlabel("Market Move (%)")
    plt.ylabel("PnL (£)")
    plt.title("Direct vs TRS PnL")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()


def plot_return_on_collateral(sim, outfile="images/trs_return_on_collateral.png"):
    x = sim["moves"] * 100
    plt.figure()
    plt.plot(x, sim["trs_roc"] * 100, label="TRS % Return on Collateral")
    plt.xlabel("Market Move (%)")
    plt.ylabel("Return on Collateral (%)")
    plt.title("TRS Return on Collateral (Hidden Leverage)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="TRS vs Direct Ownership Simulator")
    parser.add_argument("--notional", type=float, default=1_000_000)
    parser.add_argument("--financing_rate", type=float, default=0.05, help="Annual financing (e.g., 0.05 for 5%)")
    parser.add_argument("--period_years", type=float, default=1.0)
    parser.add_argument("--collateral", type=float, default=200_000)
    parser.add_argument("--move_start", type=float, default=-0.20)
    parser.add_argument("--move_stop", type=float, default=0.21)
    parser.add_argument("--move_step", type=float, default=0.05)
    args = parser.parse_args()

    ensure_dirs()
    sim = simulate_trs(
        notional=args.notional,
        financing_rate=args.financing_rate,
        period_years=args.period_years,
        collateral=args.collateral,
        move_start=args.move_start,
        move_stop=args.move_stop,
        move_step=args.move_step,
    )

    save_csv(sim)
    plot_pnl(sim)
    plot_return_on_collateral(sim)

    # Console summary
    print("Saved:")
    print("  - data/trs_results.csv")
    print("  - images/trs_pnl.png")
    print("  - images/trs_return_on_collateral.png")


if __name__ == "__main__":
    main()
