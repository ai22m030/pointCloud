import numpy as np
import open3d as o3d


def load_point_cloud(model_path):
    return o3d.io.read_point_cloud(model_path)


def visualize_point_cloud(pc, point_size=1.0):
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(pc)
    render_option = vis.get_render_option()
    render_option.point_size = point_size
    vis.run()
    vis.destroy_window()


def downsample_point_cloud(pc, voxel_size):
    return pc.voxel_down_sample(voxel_size=voxel_size)


def upsample_point_cloud(pc):
    points = np.asarray(pc.points)
    new_points = []
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i + 1]
        interpolated_points = np.linspace(p1, p2, num=2, endpoint=False)
        new_points.extend(interpolated_points)

    new_pcd = o3d.geometry.PointCloud()
    new_pcd.points = o3d.utility.Vector3dVector(new_points)
    return new_pcd


# Model
model = "model.ply"

# Load
pcd = load_point_cloud(model)

# Visualize
visualize_point_cloud(pcd, point_size=1.0)

# Downsample
downsampled_pcd = downsample_point_cloud(pcd, voxel_size=10.0)
visualize_point_cloud(downsampled_pcd, point_size=1.0)

# Upsample
upsampled_pcd = upsample_point_cloud(pcd)
visualize_point_cloud(upsampled_pcd, point_size=1.0)
