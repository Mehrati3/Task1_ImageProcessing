import sys
import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QGraphicsScene
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2

class MplCanvas(FigureCanvas):
    """ Custom Matplotlib Canvas to Embed into PyQt5 """
    def __init__(self, parent=None):
        fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_xlabel("Intensity")  # X-axis label
        self.ax.set_ylabel("Frequency")  # Y-axis label
        self.ax.set_title("Histogram of Image Intensity")  # Title
        super().__init__(fig)

class ImageApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        # Load UI file
        uic.loadUi("ui.ui", self)  # Ensure "ui.ui" is in the same folder

        # Connect button click to generate image
        self.btn_generate.clicked.connect(self.generate_image)

        self.wrapbutton.clicked.connect(self.wrap_image)
        

        # Set up PyQtGraph in QGraphicsView
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.img_item = pg.ImageItem()
        self.scene.addItem(self.img_item)

        # Setup Matplotlib Histogram inside the Grid Layout
        self.canvas = MplCanvas(self)
        self.gridLayout.addWidget(self.canvas, 0, 0)  # Add canvas to grid layout

    

    

    def wrap_image(self):
        """ Applies a wavy distortion effect to the chessboard. """

        size = 512  # Image size
        rows, cols = 6, 6  # Chessboard size
        square_size = size // rows  # Size of each square

        # Create the base chessboard with green shades
        image = np.ones((size, size, 3), dtype=np.uint8) * 255  
        green_shades = np.linspace(30, 220, rows).astype(np.uint8)  

        for i in range(rows):
            for j in range(cols):
                if (i + j) % 2 == 1:  # Chessboard pattern
                    y_start, y_end = i * square_size, (i + 1) * square_size
                    x_start, x_end = j * square_size, (j + 1) * square_size
                    image[y_start:y_end, x_start:x_end] = [0, green_shades[i], 0]  

        # Create distortion maps for x and y coordinates
        map_x, map_y = np.meshgrid(np.arange(size), np.arange(size), indexing='xy')

        # Introduce sinusoidal and random distortions
        strength_x = 15  # Adjust for more or less warping in x-direction
        strength_y = 20  # Adjust for more or less warping in y-direction
        frequency = 500   # Frequency of the waves

        # Apply wavy distortion
        map_x = map_x + strength_x * np.sin(2 * np.pi * map_y / frequency) + np.random.uniform(0, 0, (size, size))
        map_y = map_y + strength_y * np.sin(2 * np.pi * map_x / frequency) + np.random.uniform(0, 0, (size, size))

        # Apply remapping (warp transformation)
        wrapped_image = cv2.remap(image, map_x.astype(np.float32), map_y.astype(np.float32), interpolation=cv2.INTER_LINEAR)

        # Display the warped image in PyQtGraph
        self.img_item.setImage(wrapped_image)

    

    def generate_image(self):
        size = 512  # Image size
        rows, cols = 6, 6  # Chessboard size
        square_size = size // rows  # Size of each square

        # Create an empty image (white background)
        image = np.ones((size, size, 3), dtype=np.uint8) * 255  

        # Generate green shades from dark (low intensity) to bright (high intensity)
        green_shades = np.linspace(30, 220, rows).astype(np.uint8)  # Adjusted intensity range

        for i in range(rows):
            for j in range(cols):
                if (i + j) % 2 == 1:  # Chessboard pattern (green squares)
                    y_start, y_end = i * square_size, (i + 1) * square_size
                    x_start, x_end = j * square_size, (j + 1) * square_size
                    image[y_start:y_end, x_start:x_end] = [0, green_shades[i], 0]  # Green variation

        # Convert image to grayscale
        image_gray = np.dot(image, [0.2989, 0.587, 0.114]).flatten()
        N = len(image_gray)
        
        # Compute Mean
        mean_value = sum(image_gray) / N
        
        # Compute Standard Deviation
        sum_squared_diff = sum((x - mean_value) ** 2 for x in image_gray)
        std_dev = (sum_squared_diff / N) ** 0.5

        # Update QLabel values
        self.label_mean.setText(f"{mean_value:.2f}")
        self.label_stddev.setText(f"{std_dev:.2f}")

        # Convert image for PyQtGraph and display it
        self.img_item.setImage(image)

        # Show histogram inside the Grid Layout with Axis Labels
        self.update_histogram(image)

        

    def update_histogram(self, image):
        grayscale = np.dot(image, [0.2989, 0.587, 0.114])  # Convert to grayscale
        
        self.canvas.ax.clear()  # Clear previous histogram

        # Define intensity bins: 10 bins covering 0-255 range
        bins = np.linspace(0, 255, 11)  # 10 bins: [0-25.5], [25.5-51], ..., [229.5-255]
        
        self.canvas.ax.hist(grayscale.ravel(), bins=bins, color="green", edgecolor="black", alpha=0.75)

        # Grid and Formatting
        self.canvas.ax.set_xlabel("Intensity (0-255)")  
        self.canvas.ax.set_ylabel("Frequency")  
        self.canvas.ax.set_title("Histogram of Image Intensity")
        self.canvas.ax.grid(True, linestyle="--", alpha=0.6)

        self.canvas.draw()  # Update the plot


# Run the Application
app = QtWidgets.QApplication(sys.argv)
window = ImageApp()
window.show()
sys.exit(app.exec_())  # Keeps the app running
