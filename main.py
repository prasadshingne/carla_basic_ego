#!/usr/bin/env python3

import argparse
import csv
import math
import os
import sys
import time

import carla


def get_speed_kmh(velocity):
    """Return speed in kilometers per hour from carla.Vector3D."""
    return 3.6 * math.sqrt(
        velocity.x * velocity.x +
        velocity.y * velocity.y +
        velocity.z * velocity.z
    )


def main():
    parser = argparse.ArgumentParser(description="Basic Carla ego vehicle demo")
    parser.add_argument("--host", default="127.0.0.1", help="Carla server IP")
    parser.add_argument("--port", type=int, default=2000, help="Carla server port")
    parser.add_argument("--town", default=None, help="Town name for Carla world")
    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Simulation duration in seconds",
    )
    args = parser.parse_args()

    # Prepare output folders
    frames_dir = os.path.join("output", "frames")
    metrics_dir = os.path.join("output", "metrics")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(metrics_dir, exist_ok=True)
    metrics_path = os.path.join(metrics_dir, "metrics.csv")

    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)

    vehicle = None
    camera = None
    actors = []

    world = None
    original_settings = None

    try:
        print("Connecting to Carla at {}:{} ...".format(args.host, args.port))
        world = client.get_world()

        if args.town is not None and world.get_map().name != args.town:
            print("Loading town {} ...".format(args.town))
            world = client.load_world(args.town)

        # Switch world to synchronous mode for repeatable behavior
        original_settings = world.get_settings()
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)

        # Setup traffic manager
        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)

        blueprint_library = world.get_blueprint_library()

        # Choose a vehicle blueprint
        vehicle_bp_candidates = blueprint_library.filter("vehicle.tesla.model3")
        if not vehicle_bp_candidates:
            vehicle_bp_candidates = blueprint_library.filter("vehicle.*")

        vehicle_bp = vehicle_bp_candidates[0]
        vehicle_bp.set_attribute("role_name", "ego")

        spawn_points = world.get_map().get_spawn_points()
        if not spawn_points:
            print("No spawn points found")
            return

        spawn_point = spawn_points[0]

        print("Spawning ego vehicle...")
        vehicle = world.spawn_actor(vehicle_bp, spawn_point)
        actors.append(vehicle)

        # Enable autopilot on traffic manager
        vehicle.set_autopilot(True, traffic_manager.get_port())

        # Attach RGB camera
        camera_bp = blueprint_library.find("sensor.camera.rgb")
        camera_bp.set_attribute("image_size_x", "800")
        camera_bp.set_attribute("image_size_y", "600")
        camera_bp.set_attribute("fov", "90")

        camera_transform = carla.Transform(
            carla.Location(x=0.8, z=1.7)
        )
        camera = world.spawn_actor(
            camera_bp, camera_transform, attach_to=vehicle
        )
        actors.append(camera)

        # Camera callback to save frames
        def save_image(image):
            filename = os.path.join(frames_dir, "{:06d}.png".format(image.frame))
            image.save_to_disk(filename)

        camera.listen(save_image)

        # Open csv for metrics logging
        csv_file = open(metrics_path, mode="w", newline="")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "sim_time",
                "frame",
                "speed_kmh",
                "throttle",
                "steer",
                "brake",
                "gear",
            ]
        )

        print("Running simulation for {:.1f} seconds".format(args.duration))
        start_time = time.time()
        sim_time = 0.0

        while sim_time < args.duration:
            world.tick()
            sim_time = time.time() - start_time

            if vehicle is not None:
                velocity = vehicle.get_velocity()
                control = vehicle.get_control()
                speed_kmh = get_speed_kmh(velocity)

                csv_writer.writerow(
                    [
                        "{:.3f}".format(sim_time),
                        world.get_snapshot().frame,
                        "{:.3f}".format(speed_kmh),
                        "{:.3f}".format(control.throttle),
                        "{:.3f}".format(control.steer),
                        "{:.3f}".format(control.brake),
                        control.gear,
                    ]
                )

        csv_file.close()
        print("Done. Frames stored in {}, metrics stored at {}".format(frames_dir, metrics_path))

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print("Error:", e)
    finally:
        print("Cleaning up actors")
        try:
            if camera is not None:
                camera.stop()
        except Exception:
            pass

        if actors:
            client.apply_batch([carla.command.DestroyActor(a) for a in actors])

        if world is not None and original_settings is not None:
            world.apply_settings(original_settings)


if __name__ == "__main__":
    main()

