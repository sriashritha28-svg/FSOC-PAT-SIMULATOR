import csv
import json
import matplotlib.pyplot as plt

class ReportExporter:
    """Generates standardized CSV, JSON, and graphical performance reports for SIH evaluation."""
    
    @staticmethod
    def export_csv(filepath: str, metrics: dict, params: dict):
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Metric / Parameter", "Value"])
            for k, v in metrics.items():
                writer.writerow([k, v])
            writer.writerow([])
            writer.writerow(["--- CONFIGURATION PARAMETERS ---", ""])
            for k, v in params.items():
                writer.writerow([k, str(v)])

    @staticmethod
    def export_json(filepath: str, metrics: dict, params: dict):
        payload = {
            "performance_metrics": metrics,
            "configuration_parameters": params
        }
        with open(filepath, 'w') as f:
            json.dump(payload, f, indent=4)

    @staticmethod
    def export_plots(filepath: str, error_history: list, fps_history: list):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        ax1.plot(error_history, color='red', label='Tracking Error (px)')
        ax1.set_ylabel('Error (Pixels)')
        ax1.set_title('FSOC Pointing Error Over Time')
        ax1.grid(True)
        ax1.legend()
        
        ax2.plot(fps_history, color='green', label='Processing FPS')
        ax2.set_xlabel('Frame Index')
        ax2.set_ylabel('Frames Per Second')
        ax2.set_title('System Processing Throughput')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()