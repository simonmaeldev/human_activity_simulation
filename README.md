# Human Activity Simulation

A simulation of human activity and its environmental impact.

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On Linux/macOS:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the simulation:
```bash
python main.py
```
This will run a 100-day simulation with default parameters.

2. Create animations from simulation data:
```bash
python visualization/create_animations.py simulation_data/dir_name
```
This will generate two animations:
- grid_animation.mp4: Shows the evolution of the grid state
- pollution_animation.mp4: Shows the evolution of pollution levels

The animations will be saved in the specified simulation data directory.

