"""
TGA Data Analyzer - Correct Version for Your Data Format
Handles time-based TGA data with temperature ramping
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


class TGAAnalyzerCorrect:
    """TGA data analyzer for time-based thermal analysis data"""

    def __init__(self):
        self.raw_data = {}
        self.tga_results = {}
        self.summary_table = None

        print("TGA Data Analyzer - Correct Version")
        print("=" * 50)
        print("Handles time-based TGA data with temperature ramping")
        print()

    def load_tga_folder(self, folder_path=None):
        """Load all TGA files from folder"""
        if folder_path is None:
            folder_path = r"D:\Master\540.635 Software\mechtherm_analytics\tga data"

        if not os.path.exists(folder_path):
            print(f"Folder not found: {folder_path}")
            return False

        # Find all CSV files
        files = glob.glob(os.path.join(folder_path, "*.csv"))

        if not files:
            print("No CSV files found in folder")
            return False

        print(f"Found {len(files)} TGA files:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {Path(file).name}")

        success_count = 0
        for filepath in files:
            filename = Path(filepath).name
            sample_name = self._extract_sample_name(filename)

            print(f"\nProcessing: {filename}")
            print(f"Sample name: {sample_name}")

            if self._load_single_tga_file(filepath, sample_name):
                success_count += 1

        print(f"\nSuccessfully loaded {success_count}/{len(files)} files")
        return success_count > 0

    def _extract_sample_name(self, filename):
        """Extract meaningful sample name from filename"""
        # Remove extension and extract key parts
        base_name = Path(filename).stem

        # Extract key information from filename like "9.30_tga_mek_5%_fabric_930"
        parts = base_name.split('_')

        # Try to identify sample type
        sample_parts = []
        for part in parts:
            if 'mek' in part.lower():
                sample_parts.append('MEK')
            elif '%' in part:
                sample_parts.append(part)
            elif 'fabric' in part.lower():
                sample_parts.append('Fabric')
            elif 'bulk' in part.lower():
                sample_parts.append('Bulk')

        if sample_parts:
            return '-'.join(sample_parts)
        else:
            return base_name

    def _load_single_tga_file(self, filepath, sample_name):
        """Load single TGA file with correct column mapping"""
        try:
            df = pd.read_csv(filepath)

            # Extract the correct columns
            time = df['Time'].values  # Time in minutes
            weight = df['Unsubtracted Weight'].values  # Weight in mg
            temperature = df['Sample Temperature'].values  # Temperature in °C

            # Remove any NaN values
            valid_mask = ~(np.isnan(time) | np.isnan(weight) | np.isnan(temperature))
            time = time[valid_mask]
            weight = weight[valid_mask]
            temperature = temperature[valid_mask]

            # Convert weight to percentage (relative to initial weight)
            initial_weight = weight[0]
            weight_percent = (weight / initial_weight) * 100

            # Calculate derivative (dW/dT)
            deriv_weight = self._calculate_derivative(temperature, weight_percent)

            # Store data
            self.raw_data[sample_name] = {
                'time': time,
                'temperature': temperature,
                'weight_percent': weight_percent,
                'weight_mg': weight,
                'deriv_weight': deriv_weight,
                'filepath': filepath
            }

            # Analyze thermal events
            results = self._analyze_thermal_events(temperature, weight_percent, deriv_weight)
            self.tga_results[sample_name] = results

            print(f"  Loaded {len(time)} data points")
            print(f"  Temperature range: {temperature.min():.0f} to {temperature.max():.0f}°C")
            print(f"  Weight loss: {100 - weight_percent.min():.1f}%")
            print(f"  T5: {results['T5']:.0f}°C, T50: {results['T50']:.0f}°C, Tmax: {results['Tmax']:.0f}°C")

            return True

        except Exception as e:
            print(f"  Error loading {filepath}: {e}")
            return False

    def _calculate_derivative(self, temperature, weight_percent):
        """Calculate dW/dT derivative"""
        deriv = np.zeros_like(weight_percent)

        for i in range(1, len(weight_percent) - 1):
            dt = temperature[i + 1] - temperature[i - 1]
            dw = weight_percent[i + 1] - weight_percent[i - 1]
            if dt > 0:
                deriv[i] = dw / dt

        # Handle endpoints
        if len(weight_percent) > 1:
            dt_start = temperature[1] - temperature[0]
            if dt_start > 0:
                deriv[0] = (weight_percent[1] - weight_percent[0]) / dt_start

            dt_end = temperature[-1] - temperature[-2]
            if dt_end > 0:
                deriv[-1] = (weight_percent[-1] - weight_percent[-2]) / dt_end

        return deriv

    def _analyze_thermal_events(self, temperature, weight_percent, deriv_weight):
        """Analyze thermal decomposition events"""
        results = {}

        # T5: Temperature at 5% weight loss (95% remaining)
        try:
            indices_95 = np.where(weight_percent <= 95.0)[0]
            if len(indices_95) > 0:
                results['T5'] = temperature[indices_95[0]]
            else:
                results['T5'] = np.nan
        except:
            results['T5'] = np.nan

        # T50: Temperature at 50% weight loss
        try:
            indices_50 = np.where(weight_percent <= 50.0)[0]
            if len(indices_50) > 0:
                results['T50'] = temperature[indices_50[0]]
            else:
                results['T50'] = np.nan
        except:
            results['T50'] = np.nan

        # Tmax: Temperature at maximum decomposition rate (minimum derivative)
        try:
            # Only consider temperature range where significant decomposition occurs
            decomp_mask = (temperature >= 200) & (temperature <= 600)
            if np.any(decomp_mask):
                decomp_deriv = deriv_weight[decomp_mask]
                decomp_temp = temperature[decomp_mask]

                if len(decomp_deriv) > 0:
                    min_deriv_idx = np.argmin(decomp_deriv)
                    results['Tmax'] = decomp_temp[min_deriv_idx]
                else:
                    results['Tmax'] = np.nan
            else:
                results['Tmax'] = np.nan
        except:
            results['Tmax'] = np.nan

        # Residue at 600°C
        try:
            if temperature.max() >= 600:
                idx_600 = np.where(temperature >= 600)[0]
                if len(idx_600) > 0:
                    results['Residue_600C'] = weight_percent[idx_600[0]]
                else:
                    results['Residue_600C'] = weight_percent[-1]
            else:
                results['Residue_600C'] = weight_percent[-1]
        except:
            results['Residue_600C'] = weight_percent[-1] if len(weight_percent) > 0 else np.nan

        return results

    def generate_summary_table(self):
        """Generate summary table of TGA results"""
        if not self.tga_results:
            print("No TGA data analyzed yet!")
            return

        print("\nTGA ANALYSIS SUMMARY")
        print("=" * 70)

        # Create summary data
        summary_data = []
        for sample_name, results in self.tga_results.items():
            summary_data.append({
                'Sample': sample_name,
                'T5_C': results['T5'],
                'T50_C': results['T50'],
                'Tmax_C': results['Tmax'],
                'Residue_600C_percent': results['Residue_600C']
            })

        self.summary_table = pd.DataFrame(summary_data)

        # Display table
        print("TGA Data")
        print("-" * 70)
        print(f"{'Sample':<25} {'T5 [°C]':<8} {'T50 [°C]':<9} {'Tmax [°C]':<10} {'Residue [%]':<12}")
        print("-" * 70)

        for _, row in self.summary_table.iterrows():
            sample = row['Sample'][:24]
            t5 = f"{row['T5_C']:.0f}" if not pd.isna(row['T5_C']) else "N/A"
            t50 = f"{row['T50_C']:.0f}" if not pd.isna(row['T50_C']) else "N/A"
            tmax = f"{row['Tmax_C']:.0f}" if not pd.isna(row['Tmax_C']) else "N/A"
            residue = f"{row['Residue_600C_percent']:.1f}" if not pd.isna(row['Residue_600C_percent']) else "N/A"

            print(f"{sample:<25} {t5:<8} {t50:<9} {tmax:<10} {residue:<12}")

        print("-" * 70)
        return self.summary_table

    def plot_tga_curves(self, title=None, figsize=(12, 5)):
        """Plot TGA curves (weight loss and derivative)"""
        if not self.raw_data:
            print("No TGA data to plot!")
            return

        print("\nGENERATING TGA PLOTS")
        print("=" * 50)

        if title is None:
            title = input("Enter plot title [default: TGA curves for polyurethane films]: ").strip()
            if not title:
                title = "TGA curves for polyurethane films"

        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Define colors and line styles
        colors = ['#d62728', '#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b', '#17becf', '#bcbd22']
        line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':']

        # Plot weight loss curves
        for i, (sample_name, data) in enumerate(self.raw_data.items()):
            color = colors[i % len(colors)]
            line_style = line_styles[i % len(line_styles)]

            # Weight loss plot
            ax1.plot(data['temperature'], data['weight_percent'],
                     color=color, linestyle=line_style, linewidth=2.5,
                     label=sample_name, alpha=0.9)

            # Derivative plot (use absolute value for positive peaks)
            ax2.plot(data['temperature'], -data['deriv_weight'],  # Negative for conventional display
                     color=color, linestyle=line_style, linewidth=2.5,
                     label=sample_name, alpha=0.9)

        # Format weight loss plot
        ax1.set_xlabel('Temperature (°C)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Weight %', fontsize=12, fontweight='bold')
        ax1.set_xlim(0, 600)
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10, frameon=True, loc='upper right')

        # Format derivative plot
        ax2.set_xlabel('Temperature (°C)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Deriv. Weight (%/°C)', fontsize=12, fontweight='bold')
        ax2.set_xlim(0, 700)
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10, frameon=True, loc='upper right')

        # Overall formatting
        plt.suptitle(title, fontsize=14, fontweight='bold')

        # Set borders
        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_linewidth(1.2)
                spine.set_color('black')
            ax.tick_params(labelsize=11, width=1.2)

        plt.tight_layout()

        # Save plot
        save_path = f"{title.replace(' ', '_').replace(':', '').replace(',', '')}.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"TGA plots saved to: {save_path}")

        plt.show()

    def export_results(self, filename=None):
        """Export TGA results to Excel"""
        if filename is None:
            filename = "tga_analysis_results.xlsx"

        print(f"\nEXPORTING TGA RESULTS TO: {filename}")
        print("=" * 50)

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary table
            if self.summary_table is not None:
                self.summary_table.to_excel(writer, sheet_name='TGA_Summary', index=False)

            # Raw data for each sample
            for sample_name, data in self.raw_data.items():
                df_raw = pd.DataFrame({
                    'Time_min': data['time'],
                    'Temperature_C': data['temperature'],
                    'Weight_percent': data['weight_percent'],
                    'Weight_mg': data['weight_mg'],
                    'Deriv_Weight': data['deriv_weight']
                })

                sheet_name = sample_name.replace(' ', '_').replace('%', 'pct')[:31]
                df_raw.to_excel(writer, sheet_name=sheet_name, index=False)

        print("Results exported successfully!")
        print("Excel file contains:")
        print("   • TGA_Summary - Summary table with T5, T50, Tmax")
        print("   • Individual sheets - Raw data for each sample")

    def complete_tga_analysis(self):
        """Complete TGA analysis workflow"""
        print("COMPLETE TGA ANALYSIS")
        print("=" * 60)

        # Load TGA data
        if not self.load_tga_folder():
            print("No TGA data loaded. Exiting.")
            return

        # Generate summary table
        self.generate_summary_table()

        # Plot TGA curves
        self.plot_tga_curves()

        # Export results
        self.export_results()

        print("\nTGA ANALYSIS COMPLETED!")
        print("=" * 60)


def main():
    """Main function"""
    analyzer = TGAAnalyzerCorrect()
    analyzer.complete_tga_analysis()


if __name__ == "__main__":
    main()