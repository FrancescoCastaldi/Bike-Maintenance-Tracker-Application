# Bike Maintenance Tracker Application

## Overview

The Bike Maintenance Tracker is a command-line application designed to assist cycling enthusiasts in maintaining and managing their road bikes. This application allows users to add, view, and update maintenance records, track the weight of the bike, and monitor the wear levels of various components. By providing a structured and easy-to-use interface, it ensures that users can keep their bikes in optimal condition.

As an alternative to the console workflow, the project now also offers a modern graphical interface powered by [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) that reads and writes the same data files (`records.txt` and `components.txt`).

## Features

- **Maintenance Records Management:**
  - Add new maintenance records with the date and a detailed description of the service performed.
  - View a list of all maintenance records to keep track of past services.

- **Bike Weight Tracking:**
  - Update and store the weight of the bike.
  - View the current weight of the bike.

- **Component Wear Level Monitoring:**
  - View the wear levels of key bike components, including tires, inner tubes, derailleur cables, brake cables, and handlebar tape.
  - Update the wear levels of each component to ensure timely replacements and maintenance.

## Interfaccia Grafica (Windows, macOS e Linux)

### Prerequisiti

- [Python 3.9+](https://www.python.org/downloads/)
- Accesso a Internet per consentire a `pip` di installare il tema grafico `ttkbootstrap`

### Avvio manuale (tutte le piattaforme)

All'interno della cartella del progetto eseguire i seguenti comandi:

```bash
python -m venv .venv-gui
source .venv-gui/bin/activate  # Su Windows usare: .venv-gui\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python bike_maintenance_gui.py
```

### Avvio rapido su Windows

Per automatizzare l'installazione delle dipendenze e l'avvio dell'applicazione grafica è disponibile lo script `run_gui.bat`. Eseguire:

```bat
run_gui.bat
```

Lo script crea (se necessario) un ambiente virtuale locale, installa le dipendenze definite in `requirements.txt` e avvia l'interfaccia grafica.

## Esecuzione su Windows con PowerShell

Per facilitare l'esecuzione dell'applicazione su Windows è stato aggiunto lo script `run.ps1`, pensato per l'uso in PowerShell.

### Prerequisiti

1. Installare un compilatore C disponibile da PowerShell, come **Mingw-w64 (gcc)** oppure **LLVM (clang)**, e assicurarsi che il comando scelto sia presente nella variabile d'ambiente `PATH`.
2. Se PowerShell blocca l'esecuzione degli script, aprire una finestra di PowerShell e abilitare temporaneamente l'esecuzione con:

   ```powershell
   Set-ExecutionPolicy -Scope Process RemoteSigned
   ```

### Compilazione ed esecuzione

All'interno della cartella del progetto eseguire:

```powershell
./run.ps1
```

Lo script individua automaticamente il compilatore disponibile (`gcc` o `clang`), compila `bike_track.c` generando `bike_track.exe` (ricompilando solo se necessario) e avvia l'applicazione. È possibile forzare una ricompilazione completa con il parametro `-Clean`:

```powershell
./run.ps1 -Clean
```

## Implementation Details

The application is developed in C, leveraging standard input/output functions to interact with the user and file handling to persist data. The main components of the application include:

- **Data Structures:** Use of structured data types (`struct`) to define maintenance records and bike components.
- **File Handling:** Efficient reading and writing to text files (`records.txt` and `components.txt`) to ensure data persistence across sessions.
- **User Interface:** A simple menu-driven interface that guides the user through various operations like adding records, updating weight, and viewing components.

## Creation Process

1. **Requirements Gathering:**
   - Identified the key features needed for effective bike maintenance management.

2. **Design:**
   - Structured the application into modular functions for adding, viewing, and updating records.
   - Defined data structures for maintenance records and bike components.

3. **Implementation:**
   - Developed the core functionalities using C programming language.
   - Implemented file operations to ensure data persistence, creating or updating files as necessary.
   - Incorporated input validation and error handling to enhance user experience and application reliability.

4. **Testing and Refinement:**
   - Conducted thorough testing to ensure all functionalities work as expected.
   - Refined the code to handle edge cases and improve performance.

5. **Documentation:**
   - Documented the code with comments for maintainability and provided user instructions for running the application.

This structured approach ensured that the application not only meets user needs but is also robust and reliable, providing a valuable tool for bike maintenance enthusiasts.
