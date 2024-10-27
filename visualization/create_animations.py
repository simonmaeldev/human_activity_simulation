import sys
from grid_animator import GridAnimator

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_animations.py <simulation_data_directory>")
        return 1
        
    data_dir = sys.argv[1]
    
    try:
        animator = GridAnimator(data_dir)
        print("Creating grid animation...")
        animator.animate_grid()
        print("Creating pollution animation...")
        animator.animate_pollution()
        print("Animations created successfully!")
        return 0
    except Exception as e:
        print(f"Error creating animations: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
