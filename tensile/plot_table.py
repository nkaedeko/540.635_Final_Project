"""
Complete Tensile Testing Analyzer
Complete tensile testing analyzer - handles replicate trials and generates both plots and statistical tables
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path
import re


class CompleteTensileAnalyzer:
    """Complete tensile testing analyzer"""

    def __init__(self):
        self.raw_trials = {}  # Store raw data for each trial
        self.sample_groups = {}  # Group by sample type
        self.statistical_summary = None

        print("Complete Tensile Testing Analyzer")
        print("=" * 50)
        print("Handles multiple trials and generates both plots and statistical tables")
        print()

    def load_files(self):
        """Load files"""
        print("File Loading Options:")
        print("1. Load files from current directory")
        print("2. Load files from specific folder")
        print("3. Load individual files")

        choice = input("Choose option (1/2/3) [1]: ").strip() or "1"

        if choice == "1":
            return self._load_from_current_directory()
        elif choice == "2":
            return self._load_from_folder()
        else:
            return self._load_individual_files()

    def _load_from_current_directory(self):
        """Load from current directory"""
        files = glob.glob("*.txt") + glob.glob("*.csv")

        if not files:
            print("No data files found in current directory")
            return False

        print(f"\nFound {len(files)} files:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {file}")

        return self._process_files(files)

    def _load_from_folder(self):
        """Load from specified folder"""
        folder = input("Enter folder path: ").strip().strip('"')
        if not os.path.exists(folder):
            print("Folder not found")
            return False

        files = glob.glob(os.path.join(folder, "*.txt")) + glob.glob(os.path.join(folder, "*.csv"))

        if not files:
            print("No data files found")
            return False

        return self._process_files(files)

    def _load_individual_files(self):
        """Load individual files one by one"""
        files = []
        while True:
            filepath = input(f"Enter file path {len(files) + 1} (or press Enter to finish): ").strip().strip('"')
            if not filepath:
                break
            if os.path.exists(filepath):
                files.append(filepath)
            else:
                print("File not found")

        return self._process_files(files) if files else False

    def _process_files(self, files):
        """Process file list - input parameters for each file individually"""
        if not files:
            return False

        print(f"\nProcessing {len(files)} files...")
        print("You will be asked for parameters for each file individually.")

        # Base sample name (shared by all files)
        base_sample_name = input("Enter base sample name (e.g., MEK-Si-Bulk-1.25%): ").strip()
        if not base_sample_name:
            base_sample_name = "Sample"

        # Process each file
        success_count = 0
        for i, filepath in enumerate(files):
            filename = Path(filepath).name
            trial_name = f"Run {i + 1}"

            print(f"\nProcessing file {i + 1}/{len(files)}: {filename}")
            print(f"This will be labeled as: {base_sample_name} - {trial_name}")

            # Input parameters for each file individually
            print(f"\nEnter parameters for {filename}:")
            gauge_length = self._get_float_input("Gauge length (mm)", 30.00)
            cross_section_area = self._get_float_input("Cross-sectional area (mm²)", 3.00)

            # Confirm parameters
            print(f"Confirmed {filename}: GL={gauge_length}mm, Area={cross_section_area}mm²")

            if self._load_single_file(filepath, base_sample_name, trial_name, gauge_length, cross_section_area):
                success_count += 1

        print(f"\nSuccessfully loaded {success_count}/{len(files)} files")
        return success_count > 0

    def _get_float_input(self, prompt, default):
        """Get float input from user"""
        while True:
            value = input(f"{prompt} [default: {default}]: ").strip()
            if not value:
                return default
            try:
                return float(value)
            except ValueError:
                print("Please enter a valid number")

    def _load_single_file(self, filepath, sample_name, trial_name, gauge_length, cross_section_area):
        """Load single file"""
        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Find data start line
            data_start = 0
            for i, line in enumerate(lines):
                line_clean = line.strip().lower()
                if any(keyword in line_clean for keyword in ['crosshead', 'load', 'time', 'extension', 'force']):
                    continue
                if line_clean and (line_clean[0].isdigit() or line_clean[0] == '-'):
                    data_start = i
                    break

            # Parse data
            data_rows = []
            for i in range(data_start, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue

                try:
                    # Try different delimiters
                    for delimiter in ['\t', ',', ' ']:
                        parts = line.replace(',', '.').split(delimiter)
                        parts = [p.strip() for p in parts if p.strip()]

                        if len(parts) >= 3:
                            crosshead = float(parts[0])
                            load = float(parts[1])
                            time = float(parts[2])
                            data_rows.append([crosshead, load, time])
                            break
                except (ValueError, IndexError):
                    continue

            if len(data_rows) < 10:
                print(f"  Insufficient data points ({len(data_rows)})")
                return False

            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=['crosshead', 'load', 'time'])

            # Calculate stress and strain
            df['strain'] = df['crosshead'] / gauge_length
            df['stress'] = df['load'] / cross_section_area

            # Calculate properties
            properties = self._calculate_properties(df)

            # Store data
            full_name = f"{sample_name}_{trial_name}"
            self.raw_trials[full_name] = {
                'data': df,
                'properties': properties,
                'sample_name': sample_name,
                'trial_name': trial_name,
                'gauge_length': gauge_length,
                'cross_section_area': cross_section_area,
                'filepath': filepath
            }

            # Group by sample
            if sample_name not in self.sample_groups:
                self.sample_groups[sample_name] = []
            self.sample_groups[sample_name].append({
                'trial_name': trial_name,
                'full_name': full_name,
                **properties
            })

            print(
                f"  Loaded {len(df)} points - UTS: {properties['UTS_MPa']:.2f} MPa, E: {properties['Youngs_Modulus_MPa']:.1f} MPa")
            return True

        except Exception as e:
            print(f"  Error: {e}")
            return False

    def _calculate_properties(self, data, strain_range=(0.001, 0.005)):
        """Calculate mechanical properties"""
        properties = {}

        # Young's modulus
        mask = (data['strain'] >= strain_range[0]) & (data['strain'] <= strain_range[1])
        linear_data = data[mask]

        if len(linear_data) >= 5:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                linear_data['strain'], linear_data['stress']
            )
            properties['Youngs_Modulus_MPa'] = slope
            properties['R_squared'] = r_value ** 2
        elif len(data) >= 5:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                data['strain'], data['stress']
            )
            properties['Youngs_Modulus_MPa'] = slope
            properties['R_squared'] = r_value ** 2
        else:
            properties['Youngs_Modulus_MPa'] = 0
            properties['R_squared'] = 0

        # Other properties
        properties['UTS_MPa'] = data['stress'].max()
        properties['Strain_at_Break_percent'] = data['strain'].iloc[-1] * 100
        properties['Max_Load_N'] = data['load'].max()
        properties['Max_Displacement_mm'] = data['crosshead'].max()

        # Toughness
        try:
            properties['Toughness_MJ_per_m3'] = np.trapezoid(data['stress'], data['strain'])
        except AttributeError:
            properties['Toughness_MJ_per_m3'] = np.trapz(data['stress'], data['strain'])

        return properties

    def calculate_statistics(self):
        """Calculate statistical summary"""
        print("\nCALCULATING STATISTICAL SUMMARY")
        print("=" * 50)

        summary_data = []

        for sample_name, trials in self.sample_groups.items():
            print(f"Analyzing {sample_name}: {len(trials)} trials")

            # Extract values
            properties = ['Youngs_Modulus_MPa', 'UTS_MPa', 'Strain_at_Break_percent', 'Toughness_MJ_per_m3']

            sample_stats = {
                'Sample': sample_name,
                'n_trials': len(trials)
            }

            for prop in properties:
                values = [trial[prop] for trial in trials]

                sample_stats[f'{prop}_mean'] = np.mean(values)
                sample_stats[f'{prop}_std'] = np.std(values, ddof=1) if len(values) > 1 else 0.0
                sample_stats[f'{prop}_cv'] = (np.std(values, ddof=1) / np.mean(values) * 100) if len(
                    values) > 1 and np.mean(values) != 0 else 0.0

            summary_data.append(sample_stats)

            # Display statistical information
            if len(trials) > 1:
                print(
                    f"  UTS: {sample_stats['UTS_MPa_mean']:.2f} ± {sample_stats['UTS_MPa_std']:.2f} MPa (CV: {sample_stats['UTS_MPa_cv']:.1f}%)")
                print(
                    f"  E: {sample_stats['Youngs_Modulus_MPa_mean']:.1f} ± {sample_stats['Youngs_Modulus_MPa_std']:.1f} MPa (CV: {sample_stats['Youngs_Modulus_MPa_cv']:.1f}%)")
            else:
                print(f"  UTS: {sample_stats['UTS_MPa_mean']:.2f} MPa (single trial)")
                print(f"  E: {sample_stats['Youngs_Modulus_MPa_mean']:.1f} MPa (single trial)")

        self.statistical_summary = pd.DataFrame(summary_data)
        print("Statistical analysis completed")
        return self.statistical_summary

    def plot_stress_strain_curves(self, title=None, figsize=(10, 8)):
        """Plot clean stress-strain curves"""
        if not self.raw_trials:
            print("No data to plot!")
            return

        print("\nGENERATING STRESS-STRAIN PLOT")
        print("=" * 50)

        if title is None:
            title = input("Enter plot title [default: Tensile Testing Results]: ").strip()
            if not title:
                title = "Tensile Testing Results"

        # Create figure
        fig, ax = plt.subplots(figsize=figsize)

        # Define styles (similar to reference figure)
        plot_styles = [
            {'color': '#d62728', 'linestyle': '-', 'linewidth': 3, 'alpha': 0.9},  # Red solid line
            {'color': '#1f77b4', 'linestyle': '--', 'linewidth': 3, 'alpha': 0.9},  # Blue dashed line
            {'color': '#2ca02c', 'linestyle': '--', 'linewidth': 2.5, 'alpha': 0.9},  # Green dashed line
            {'color': '#666666', 'linestyle': ':', 'linewidth': 2.5, 'alpha': 0.9},  # Gray dotted line
            {'color': '#ff7f0e', 'linestyle': '-.', 'linewidth': 2.5, 'alpha': 0.9},  # Orange dash-dot line
            {'color': '#9467bd', 'linestyle': '-', 'linewidth': 2.5, 'alpha': 0.9},  # Purple solid line
        ]

        # Plot each trial
        plot_index = 0
        for sample_name, trials in self.sample_groups.items():
            for trial in trials:
                trial_info = self.raw_trials[trial['full_name']]
                data = trial_info['data']
                trial_label = trial_info['trial_name']

                style = plot_styles[plot_index % len(plot_styles)]

                # Plot curve (no failure lines)
                ax.plot(data['strain'] * 100, data['stress'],
                        label=trial_label,
                        **style)

                plot_index += 1

        # Set axes
        ax.set_xlabel('Strain (%)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Stress (MPa)', fontsize=14, fontweight='bold')

        # Set axis ranges
        ax.set_xlim(0, None)
        ax.set_ylim(0, None)

        # Clean grid
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

        # Legend
        ax.legend(fontsize=12, frameon=True, fancybox=False, shadow=False,
                  framealpha=1.0, edgecolor='black', loc='lower right')

        # Set borders
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color('black')

        # Tick style
        ax.tick_params(labelsize=12, width=1.5, length=6, direction='out')

        # Background
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')

        plt.tight_layout()

        # Save plot
        save_path = f"{title.replace(' ', '_').replace('-', '_')}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print(f"Plot saved to: {save_path}")

        plt.show()

    def generate_publication_table(self, title=None):
        """Generate publication-level statistical table"""
        if self.statistical_summary is None:
            self.calculate_statistics()

        print("\nPUBLICATION TABLE")
        print("=" * 90)

        if title is None:
            title = input("Enter table title [default: Summary of engineering stress data]: ").strip()
            if not title:
                title = "Summary of engineering stress data"

        print(f"Table 1. {title}")
        print("-" * 90)
        print(f"{'Polyol':<20} {'Break strength':<18} {'Young\'s':<15} {'Toughness':<15} {'% Strain':<12} {'n':<4}")
        print(f"{'':20} {'(MPa)':<18} {'modulus':<15} {'(MJ/m³)':<15} {'':12} {'':4}")
        print(f"{'':20} {'':18} {'(MPa)':<15} {'':15} {'':12} {'':4}")
        print("-" * 90)

        # Data rows
        for _, row in self.statistical_summary.iterrows():
            sample = row['Sample'][:18]
            n_trials = int(row['n_trials'])

            if n_trials > 1:
                # Show mean ± standard deviation
                break_str = f"{row['UTS_MPa_mean']:.2f} ± {row['UTS_MPa_std']:.2f}"
                youngs = f"{row['Youngs_Modulus_MPa_mean']:.1f} ± {row['Youngs_Modulus_MPa_std']:.1f}"
                toughness = f"{row['Toughness_MJ_per_m3_mean']:.2f} ± {row['Toughness_MJ_per_m3_std']:.2f}"
                strain = f"{row['Strain_at_Break_percent_mean']:.0f} ± {row['Strain_at_Break_percent_std']:.0f}"
            else:
                # Single trial
                break_str = f"{row['UTS_MPa_mean']:.2f}"
                youngs = f"{row['Youngs_Modulus_MPa_mean']:.1f}"
                toughness = f"{row['Toughness_MJ_per_m3_mean']:.2f}"
                strain = f"{row['Strain_at_Break_percent_mean']:.0f}"

            print(f"{sample:<20} {break_str:<18} {youngs:<15} {toughness:<15} {strain:<12} {n_trials:<4}")

        print("-" * 90)
        if any(row['n_trials'] > 1 for _, row in self.statistical_summary.iterrows()):
            print("Values are presented as mean ± standard deviation where n > 1")
        print("=" * 90)

    def export_results(self, filename=None):
        """Export complete results to Excel"""
        if filename is None:
            filename = "tensile_testing_results.xlsx"

        print(f"\nEXPORTING RESULTS TO: {filename}")
        print("=" * 50)

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. Publication table
            if self.statistical_summary is not None:
                pub_data = []
                for _, row in self.statistical_summary.iterrows():
                    n_trials = int(row['n_trials'])

                    if n_trials > 1:
                        pub_data.append({
                            'Polyol': row['Sample'],
                            'Break strength (MPa)': f"{row['UTS_MPa_mean']:.2f} ± {row['UTS_MPa_std']:.2f}",
                            "Young's modulus (MPa)": f"{row['Youngs_Modulus_MPa_mean']:.1f} ± {row['Youngs_Modulus_MPa_std']:.1f}",
                            'Toughness (MJ/m³)': f"{row['Toughness_MJ_per_m3_mean']:.2f} ± {row['Toughness_MJ_per_m3_std']:.2f}",
                            '% Strain': f"{row['Strain_at_Break_percent_mean']:.0f} ± {row['Strain_at_Break_percent_std']:.0f}",
                            'n': n_trials
                        })
                    else:
                        pub_data.append({
                            'Polyol': row['Sample'],
                            'Break strength (MPa)': f"{row['UTS_MPa_mean']:.2f}",
                            "Young's modulus (MPa)": f"{row['Youngs_Modulus_MPa_mean']:.1f}",
                            'Toughness (MJ/m³)': f"{row['Toughness_MJ_per_m3_mean']:.2f}",
                            '% Strain': f"{row['Strain_at_Break_percent_mean']:.0f}",
                            'n': n_trials
                        })

                pub_df = pd.DataFrame(pub_data)
                pub_df.to_excel(writer, sheet_name='Publication_Table', index=False)

                # 2. Detailed statistics
                self.statistical_summary.to_excel(writer, sheet_name='Statistical_Summary', index=False)

            # 3. Individual trial data
            individual_data = []
            for sample_name, trials in self.sample_groups.items():
                for trial in trials:
                    trial_data = trial.copy()
                    trial_data['sample_group'] = sample_name
                    individual_data.append(trial_data)

            if individual_data:
                individual_df = pd.DataFrame(individual_data)
                individual_df.to_excel(writer, sheet_name='Individual_Trials', index=False)

        print(f"Results exported successfully!")
        print("Excel file contains:")
        print("   • Publication_Table - Ready for publication")
        print("   • Statistical_Summary - Detailed statistics")
        print("   • Individual_Trials - Each trial's data")

    def complete_analysis(self):
        """Complete analysis workflow"""
        print("COMPLETE TENSILE TESTING ANALYSIS")
        print("=" * 60)

        # 1. Load data
        if not self.load_files():
            print("No data loaded. Exiting.")
            return

        # 2. Calculate statistics
        self.calculate_statistics()

        # 3. Generate plots
        self.plot_stress_strain_curves()

        # 4. Generate statistical tables
        self.generate_publication_table()

        # 5. Export results
        self.export_results()

        print("\nCOMPLETE ANALYSIS FINISHED!")
        print("=" * 60)
        print("You now have:")
        print("  Professional stress-strain plot")
        print("  Publication-ready statistical table")
        print("  Comprehensive Excel report")


def main():
    """Main function"""
    analyzer = CompleteTensileAnalyzer()
    analyzer.complete_analysis()


if __name__ == "__main__":
    main()