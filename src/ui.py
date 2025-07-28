"""
ui.py
    
This module provides a simple graphical interface for pharmacists and
other users to run the various components of the local ML governance
lab.  It is implemented with PySimpleGUI to avoid web deployment
overheads and keep data on the local machine.  By using a local UI
bound to 127.0.0.1, the lab upholds policies that prohibit exposing
protected health information (PHI) beyond the workstation:contentReference[oaicite:18]{index=18}.
"""
    
import PySimpleGUI as sg
import threading
import subprocess
    
    
def run_command(description: str, command: list[str]):
    def worker(window: sg.Window):
        window.write_event_value('-STATUS-', f"Starting {description}…")
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                window.write_event_value('-STATUS-', f"{description} completed successfully.")
            else:
                window.write_event_value('-STATUS-', f"{description} failed: {result.stderr.strip()}")
        except Exception as e:
            window.write_event_value('-STATUS-', f"Error during {description}: {e}")

    return worker
    
    
def main():
        sg.theme('LightBlue3')
        layout = [
            [sg.Text('ML Governance Lab')],
            [sg.Button('Preflight Checks')],
            [sg.Button('Generate Synthetic Data')],
            [sg.Button('Train Baseline Model')],
            [sg.Button('Run Seismometer Evaluation')],
            [sg.Button('Simulate Drift with Evidently')],
            [sg.Button('Load Results to PostgreSQL')],
            [sg.Button('Open Grafana Dashboard')],
            [sg.Multiline(size=(80, 10), key='-OUTPUT-', autoscroll=True)],
        ]
        window = sg.Window('ML Governance Lab', layout, finalize=True)
        status_queue = []
        while True:
            event, values = window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Preflight Checks':
                threading.Thread(target=run_command('preflight checks', ['python', '-m', 'src.preflight']), args=(window,), daemon=True).start()
            elif event == 'Generate Synthetic Data':
                threading.Thread(target=run_command('synthetic data generation', ['python', '-m', 'src.synthea_generator']), args=(window,), daemon=True).start()
            elif event == 'Train Baseline Model':
                threading.Thread(target=run_command('model training', ['python', '-m', 'src.train_model']), args=(window,), daemon=True).start()
            elif event == 'Run Seismometer Evaluation':
                threading.Thread(target=run_command('seismometer evaluation', ['python', '-m', 'src.evaluate_seismometer']), args=(window,), daemon=True).start()
            elif event == 'Simulate Drift with Evidently':
                threading.Thread(target=run_command('drift monitoring', ['python', '-m', 'src.drift_monitor']), args=(window,), daemon=True).start()
            elif event == 'Load Results to PostgreSQL':
                threading.Thread(target=run_command('loading results', ['python', '-m', 'src.load_to_postgres']), args=(window,), daemon=True).start()
            elif event == 'Open Grafana Dashboard':
                # Open local Grafana page using default web browser
                import webbrowser
                webbrowser.open('http://127.0.0.1:3000')
            elif event == '-STATUS-':
                window['-OUTPUT-'].print(values['-STATUS-'])
        window.close()
    
    
if __name__ == '__main__':
        main()