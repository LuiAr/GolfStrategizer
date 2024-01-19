# Imports
import matplotlib.pyplot as plt


class GolfCourse:
    """Represents a golf course with a name, length, par, tee, and hole."""
    
    def __init__(self, name, length, par):
        """Initialize the golf course with name, length, and par."""
        self.name = name
        self.length = length 
        self.par = par
        self.tee = None
        self.hole = None

    def set_tee(self, tee):
        """Set the starting tee position for the golf course."""
        self.tee = tee

    def set_hole(self, hole):
        """Set the hole position for the golf course."""
        self.hole = hole

    def display_course_info(self):
        """Display basic information about the golf course."""
        print(f"Course: {self.name}")
        print(f"Length: {self.length} meters")
        print(f"Par: {self.par}")
        if self.tee:
            print(f"Tee: {self.tee.position}")
        if self.hole:
            print(f"Hole: {self.hole.position}")

    def display_graphically(self):
        """Display the golf course graphically using matplotlib."""
        fig, ax = plt.subplots()

        # Draw the Tee
        if self.tee:
            ax.plot(*self.tee.position, 'go')  # 'go' : green circle
            ax.text(*self.tee.position, 'Tee', verticalalignment='bottom', horizontalalignment='right')

        # Draw the Hole
        if self.hole:
            ax.plot(*self.hole.position, 'ro')  # 'ro' : red circle
            ax.text(*self.hole.position, 'Hole', verticalalignment='bottom', horizontalalignment='right')

        ax.set_xlim(0, max(self.length, self.hole.position[0] + 100))
        ax.set_ylim(0, max(self.length, self.hole.position[1] + 100))
        ax.set_title(f"{self.name} (Par {self.par})")
        plt.xlabel('Distance (meters))')
        plt.grid(True)
        plt.show()

class Tee:
    """Represents the tee (starting point) on the golf course."""
    
    def __init__(self, position):
        """Initialize the tee with its position."""
        self.position = position

class Hole:
    """Represents the hole (target) on the golf course."""
    
    def __init__(self, position):
        """Initialize the hole with its position."""
        self.position = position

# Example usage
course = GolfCourse("Ilbarritz Trou 1", 500, 5)
course.set_tee(Tee((50, 30)))
course.set_hole(Hole((450, 400)))

course.display_course_info()
course.display_graphically()
