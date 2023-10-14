import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget, QFileDialog, QComboBox
from PyQt5.QtCore import Qt
from pyntcloud import PyntCloud
import vispy.scene
from vispy.scene import visuals
import numpy as np


def load_point_cloud(file_path):
    # load the point cloud data
    cloud = PyntCloud.from_file(file_path)

    # Extracting points and colors
    points = cloud.points[['x', 'y', 'z']].to_numpy()
    colors = cloud.points[['red', 'green', 'blue']].to_numpy() / 255  # normalize colors to [0, 1]

    return points, colors


def load_pts(file_path):
    points = []
    colors = []
    with open(file_path, 'r') as file:
        for line in file:
            px, py, pz, r, g, b = map(float, line.split())
            points.append((px, py, pz))
            colors.append((r / 255, g / 255, b / 255))  # Normalize colors
    return np.array(points), np.array(colors)


def compute_depths(points, camera_position):
    return np.sqrt(np.sum((points - camera_position) ** 2, axis=1))


def apply_gradient(points, camera_position, near_color, far_color):
    depths = compute_depths(points, camera_position)
    normalized_depths = (depths - np.min(depths)) / (np.max(depths) - np.min(depths))
    gradient_colors = (1.0 - normalized_depths[:, np.newaxis]) * \
                      near_color + normalized_depths[:, np.newaxis] * far_color

    # Ensure colors are clipped within the valid range.
    gradient_colors = np.clip(gradient_colors, 0, 1)

    return gradient_colors


class PointCloudViewer(QMainWindow):
    def __init__(self):
        super().__init__(None)

        # Create a canvas with a 3d viewport
        self.canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
        self.view = self.canvas.central_widget.add_view()

        # Load your point cloud data
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "QFileDialog.getOpenFileName()",
                                                   "",
                                                   "All Files (*);;Python Files (*.py)",
                                                   options=options)

        if file_path:
            # Load point cloud data based on file extension
            _, file_extension = os.path.splitext(file_path)
            try:
                if file_extension == ".ply":
                    self.pts, self.colors = load_point_cloud(file_path)
                elif file_extension == ".pts":
                    self.pts, self.colors = load_pts(file_path)
                else:
                    raise ValueError("Unsupported file type")
            except Exception as e:
                print("An error occurred:", str(e))
                self.close()
                return

        self.backup_colors = self.colors

        # Create a scatter plot
        self.scatter = visuals.Markers()
        self.scatter.set_data(self.pts, face_color=self.colors)
        self.view.add(self.scatter)

        # Configure view
        self.view.camera = 'turntable'  # Use turntable camera

        # Set up the layout and set central widget
        layout = QVBoxLayout()
        layout.addWidget(self.canvas.native)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(10)
        self.slider.valueChanged.connect(self.update_point_size)
        layout.addWidget(self.slider)

        self.shapeComboBox = QComboBox(None)
        self.shapeComboBox.addItems(['disc', 'arrow', 'ring', 'square', 'diamond', 'cross', 'triangle_up'])
        self.shapeComboBox.currentIndexChanged.connect(self.update_point_shape)
        layout.addWidget(self.shapeComboBox)

        self.gradientComboBox = QComboBox(None)
        self.gradientComboBox.addItems(['real colors', 'gradient'])
        self.gradientComboBox.currentIndexChanged.connect(self.update_colors)
        layout.addWidget(self.gradientComboBox)

        container = QWidget(None)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setGeometry(100, 100, 800, 600)
        self.show()

    def update_colors(self):
        colors_type = self.gradientComboBox.currentText()

        if colors_type == "gradient":
            camera_position = np.array([0, 0, 0])  # Or your desired camera position
            near_color = np.array([1, 1, 1])  # White color for close points
            far_color = np.array([0, 0, 0])  # Black color for far points

            self.colors = apply_gradient(self.pts, camera_position, near_color, far_color)
        else:
            self.colors = self.backup_colors

        self.scatter.set_data(self.pts, face_color=self.colors)

    def update_point_shape(self):
        shape = self.shapeComboBox.currentText()
        self.scatter.symbol = shape

    def update_point_size(self):
        size = self.slider.value()
        self.scatter.set_data(self.pts, face_color=self.colors, size=size)


# Main execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PointCloudViewer()
    sys.exit(app.exec_())
