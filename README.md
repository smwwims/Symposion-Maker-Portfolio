# Symposion – Autonomous Service Robot (Maker Portfolio Version)

This repository is a public showcase of my **Symposion** transport robot project, created originally as my final mechatronics graduation project on top of a Festo Robotino platform. The private project repo (in German) also contained invoices and personal data, so this version focuses on the technical artefacts: **application code, mechanical CAD, and PCB design files**. It contains the **current implementation**, not the full incremental history.

## Software Overview

The main control programs for the robot are written in Festo’s proprietary environment **RobotinoView**, which combines Sequential Function Chart (SFC) and Function Block Diagram (FBD) and allows integrating **Python scripts as custom function blocks**. RobotinoView provides blocks for each integrated hardware component, libraries for robotics functions such as odometry, and mathematical operations; the entire **autonomous driving and docking logic** is implemented in this environment.

Python scripts act as intermediaries between the web interface, custom sensors, and the Robotino framework. The following scripts are used as function blocks inside the main RobotinoView program:

- `alarm.py` – triggers sound and light signals in case of an impending collision.
- `encoder.py` – passes encoder measurements to the web interface.
- `readPath.py` – retrieves permanently stored routes from a CSV file.
- `restart.py` – sends a restart signal to Robotino once it has reached the last waypoint.

Because I added custom sensors (ToF distance sensors, IR receiver/transmitter) and outputs (LED strips) that cannot be connected directly to Robotino’s I/O, I integrated an **Arduino Nano as an intermediate controller**.

- `k3_control.ino` runs continuously on the Nano, reading ToF distance values and IR receiver signals and outputting color commands as PWM signals to the LED strips.
- In parallel, `k3_communication.py` runs on Robotino’s Ubuntu-based control unit (started automatically via `startSymposion.sh`). It establishes a USB connection to the Arduino, writes distance measurements into `.txt` files that RobotinoView reads, and forwards color commands from the Flask web interface to the Arduino.

The **web interface** is built with the Flask framework. It can either talk to Robotino hardware via a REST API or write control data into `.txt` files that are consumed by the other software modules.

## Repository Structure

### `Software/`

Contains the Python scripts, Arduino code, and supporting files used alongside RobotinoView. RobotinoView project files themselves are not easily diff‑friendly, but the structure and naming of the Python and Arduino modules mirror the logical modules described in the project documentation (route following, docking, safety, communication).

### `Mechanics/`

Contains the **mechanical design files** for the robot add‑ons I designed. This includes:

- The **linear axis** mounted on top of the Robotino for the height‑adjustable platform.
- The **circular platform table** with carved bottle placements.
- The **internal platform** for additional sensors and electronics.
- Exported formats suitable for viewing (e.g., STEP) and integration into other CAD assemblies.[file:21]

Vendor parts such as the Robotino base, standard aluminum profiles, and hardware are represented using manufacturer CAD where available.[file:21]

### `Electronics/`

Contains the **PCB design artefacts** and related documentation for the custom Arduino peripheral interface board (“K3 – Arduino Peripheral IF”). This includes:

- **Schematics**
- **Board Layouts**
- **Bill of Materials (BoM)** with reference designators, descriptions, and supplier part numbers for key components (MOSFETs, connectors, resistors, capacitors, and the PCB itself).

This board interfaces 5 V sensors (ToF, IR receiver), drives LED strips, and communicates with Robotino’s control unit via USB through an Arduino Nano.

## Notes

- This repo is intended as a **readable technical snapshot** of the project, not as a polished, general‑purpose library.
- For a complete system description (mechanics, electronics, software, risk analysis, and operating manual), see the accompanying project documentation PDF.
