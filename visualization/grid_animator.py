import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap

class GridAnimator:
    """Creates animations of the simulation grid state over time"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.cell_colors = {
            'city': 'grey',
            'lake': 'blue',
            'forest': 'green',
            'land': 'yellow'
        }
        
        # Load data
        self._load_data()
        
    def _load_data(self):
        """Load all CSV files from the data directory"""
        # Load cell data for each type
        self.cell_data = {}
        for cell_type in ['city', 'forest', 'lake', 'land']:
            file_path = os.path.join(self.data_dir, f'cell_data_{cell_type}.csv')
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                if not df.empty:
                    # Pre-process position data to avoid eval() calls later
                    df['position'] = df['position'].apply(eval)
                self.cell_data[cell_type] = df
                
        # Load global metrics
        global_metrics_path = os.path.join(self.data_dir, 'global_metrics.csv')
        if os.path.exists(global_metrics_path):
            self.global_metrics = pd.read_csv(global_metrics_path)
            
        # Get grid dimensions
        all_positions = []
        for df in self.cell_data.values():
            if not df.empty:
                all_positions.extend(df['position'].tolist())
        
        if all_positions:
            x_coords, y_coords = zip(*all_positions)
            self.grid_size = (max(x_coords) + 1, max(y_coords) + 1)
        else:
            raise ValueError("No valid position data found in CSV files")
            
        # Get unique timesteps
        self.timesteps = sorted(pd.concat([df['step'] for df in self.cell_data.values()]).unique())
        
    def _create_grid_frame(self, step):
        """Create grid state for a specific timestep"""
        grid = np.zeros(self.grid_size)
        
        # Create color mapping
        color_values = {'city': 0.2, 'lake': 0.4, 'forest': 0.6, 'land': 0.8}
        
        for cell_type, df in self.cell_data.items():
            step_data = df[df['step'] == step]
            positions = step_data['position'].values
            for pos in positions:
                grid[pos[0]][pos[1]] = color_values[cell_type]
                
        return grid
        
    def _create_pollution_frame(self, step):
        """Create pollution state for a specific timestep"""
        pollution_grid = np.zeros(self.grid_size)
        
        for cell_type, df in self.cell_data.items():
            step_data = df[df['step'] == step]
            positions = step_data['position'].values
            pollution_values = step_data['air_pollution'].values
            for pos, value in zip(positions, pollution_values):
                pollution_grid[pos[0]][pos[1]] = value
                
        return pollution_grid
        
    def animate_grid(self, output_file: str = 'grid_animation.mp4'):
        """Create animation of grid state changes"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Create custom colormap for cell types
        colors = ['grey', 'blue', 'green', 'yellow']
        n_bins = 4
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        progress_bar = tqdm(total=len(self.timesteps), desc="Creating grid animation")
        
        def update(frame):
            ax.clear()
            grid = self._create_grid_frame(self.timesteps[frame])
            im = ax.imshow(grid, cmap=cmap, interpolation='nearest')
            ax.set_title(f'Simulation Step: {self.timesteps[frame]}')
            progress_bar.update(1)
            return [im]
            
        anim = FuncAnimation(fig, update, frames=len(self.timesteps),
                           interval=100, blit=True)
        progress_bar.close()
        anim.save(output_file)
        plt.close()
        
    def animate_pollution(self, output_file: str = 'pollution_animation.mp4'):
        """Create animation of pollution levels"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        progress_bar = tqdm(total=len(self.timesteps), desc="Creating pollution animation")
        
        def update(frame):
            ax.clear()
            pollution_grid = self._create_pollution_frame(self.timesteps[frame])
            im = ax.imshow(pollution_grid, cmap='RdYlBu_r', interpolation='nearest')
            
            # Add CO2 level if available
            if hasattr(self, 'global_metrics'):
                co2_data = self.global_metrics[self.global_metrics['step'] == self.timesteps[frame]]
                if not co2_data.empty:
                    co2_level = co2_data['co2_level'].iloc[0]
                    ax.set_title(f'Step: {self.timesteps[frame]} - CO2 Level: {co2_level:.2f}')
                else:
                    ax.set_title(f'Step: {self.timesteps[frame]}')
            
            # Create custom colormap from white to black for pollution
            pollution_cmap = LinearSegmentedColormap.from_list('pollution', ['white', 'black'])
            im = ax.imshow(pollution_grid, cmap=pollution_cmap, interpolation='nearest', vmin=0, vmax=100)
            plt.colorbar(im, ax=ax, label='Air Pollution Level (%)')
            progress_bar.update(1)
            return [im]
            
        anim = FuncAnimation(fig, update, frames=len(self.timesteps),
                           interval=100, blit=True)
        progress_bar.close()
        anim.save(output_file)
        plt.close()
