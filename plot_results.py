"""
Plot Results File

This file plots the results of the sensitivity analysis.
"""

import matplotlib.pyplot as plt
import pandas as pd
import os 
import numpy as np


def bar_charts():
    """""
    Builds a bar chart for VMT, VTT and k for 'Q', 'T_bar', 'D_bar', 'S_i'
    """
    parameters = ['Q', 'T_bar', 'D_bar', 'S_i']

    # Loop over the parameters and generate a bar chart.
    for param in parameters:
        # Set up the filepath to find the csv
        filepath = f"sensitivity_results/{param}_sens.csv"
        try:
            result_df = pd.read_csv(filepath)
        except:
            print(f"Parameter {param} does not have a csv")
            continue

        # Generate the 3 subplots for VMT, VTT, k
        fig, axs = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle(f"Sensitivity Analysis for {param}", fontsize=16)

        # Bar chart for VMT
        axs[0].bar(result_df[param], result_df['VMT'], color='skyblue', width=10)
        axs[0].set_title('VMT')
        axs[0].set_xlabel(param)
        axs[0].set_ylabel('Vehicle Miles Traveled (miles)')

        # Bar chart for VTT
        axs[1].bar(result_df[param], result_df['VTT'], color='salmon', width=10)
        axs[1].set_title('VTT')
        axs[1].set_xlabel(param)
        axs[1].set_ylabel('Vehicle Time Traveled (minutes)')

        # Bar chart for k
        axs[2].bar(result_df[param], result_df['k'], color='seagreen', width=10)
        axs[2].set_title('k')
        axs[2].set_xlabel(param)
        axs[2].set_ylabel('Number of Vehicles')

        plt.show()


def contour_plots():
    """
    Build the contour plots for VMT, VTT and k for varying two of 'Q', 'T_bar', 'D_bar'
    """

    parameters = ['Q', 'T_bar', 'D_bar']

    for param1 in parameters:
        for param2 in parameters:
            # Set up the filepath to find the csv
            filepath = f"sensitivity_results/cv_{param1}_{param2}_sens.csv"
            try:
                result_df = pd.read_csv(filepath)
            except:
                print(f"Parameter combination {param1, param2} does not have a csv")
                continue

            # Load CSV
            df = pd.read_csv(filepath)

            # Drop rows with missing outputs
            df = df.dropna(subset=['VMT', 'VTT', 'k'])

            # Get sorted unique parameter values
            x_vals = sorted(df[param1].unique())
            y_vals = sorted(df[param2].unique())

            # Create meshgrid
            X, Y = np.meshgrid(x_vals, y_vals)

            # Pivot data for contour values
            try:
                Z_vmt = df.pivot(index=param2, columns=param1, values='VMT').values
                Z_vtt = df.pivot(index=param2, columns=param1, values='VTT').values
                Z_k = df.pivot(index=param2, columns=param1, values='k').values
            except Exception as e:
                print(f"Skipping due to pivoting error: {e}")
                continue

            # Create subplots
            fig, axs = plt.subplots(1, 3, figsize=(17, 6))
            fig.suptitle(f"Contour Plots for {param1} vs {param2}", fontsize=16)
            levels = 15

            # Plot VMT
            c1 = axs[0].contourf(X, Y, Z_vmt, levels=levels, cmap='viridis')
            axs[0].set_title('VMT')
            axs[0].set_xlabel(param1)
            axs[0].set_ylabel(param2)
            cb1 = fig.colorbar(c1, ax=axs[0])
            cb1.set_label("VMT (miles)")

            # Plot VTT
            c2 = axs[1].contourf(X, Y, Z_vtt, levels=levels, cmap='plasma')
            axs[1].set_title('VTT')
            axs[1].set_xlabel(param1)
            axs[1].set_ylabel(param2)
            cb2 = fig.colorbar(c2, ax=axs[1])
            cb2.set_label("VTT (minutes)")

            # Plot k
            c3 = axs[2].contourf(X, Y, Z_k, levels=levels, cmap='cividis')
            axs[2].set_title('k')
            axs[2].set_xlabel(param1)
            axs[2].set_ylabel(param2)
            cb3 = fig.colorbar(c3, ax=axs[2])
            cb3.set_label("k (number of vehicles)") 

            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.show()


if __name__ == '__main__':
    bar_charts()
    contour_plots()
