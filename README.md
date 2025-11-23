# Carla Basic Ego Vehicle Demo

This project demonstrates a minimal use of the Carla Python API. The script connects to the simulator, spawns an ego vehicle, attaches an RGB camera, enables autopilot, saves camera frames, and logs motion and control values.

---

## Laptop Specs

**CPU:** Intel Core i7-11800H  
**GPU:** NVIDIA RTX A3000 Laptop GPU and Intel integrated graphics  
**Memory:** 64 GB  
**Operating System:** Ubuntu 20.04.6 LTS  
**Kernel:** 5.15.0-139-generic  
**Carla Version:** 0.9.15  
**Python Version:** 3.9+

---

## How to Run the Carla Server

From your Carla installation directory:

```bash
cd ~/Documents/CARLA_0.9.15
./CarlaUE4.sh -RenderOffScreen -quality-level=Low
```

Leave this terminal running. It is the active simulation server.

---

## How to Run the Python Demo

In a second terminal:

```bash
cd ~/Documents/projects/carla_basic_ego
python3 main.py --duration 60
```

This connects to the running Carla server and starts the ego vehicle demo.

---

## What `main.py` Does

`main.py` performs the following steps:

1. Connects to the Carla server at `127.0.0.1:2000`  
2. Loads the world and switches to synchronous mode  
3. Spawns a Tesla Model 3 (or fallback vehicle)  
4. Attaches a forward RGB camera  
5. Enables autopilot through the Traffic Manager  
6. Saves camera frames to `output/frames`  
7. Logs metrics to `output/metrics/metrics.csv` including:  
   - Simulation time  
   - Frame index  
   - Speed (km/h)  
   - Throttle  
   - Steering  
   - Brake  
   - Gear  

---

## Output Structure

```text
output/
    frames/
        .gitkeep
        (image files saved here)
    metrics/
        .gitkeep
        metrics.csv
```

---

## Repository Structure

```text
carla_basic_ego/
    main.py
    README.md
    .gitignore
    output/
        frames/
            .gitkeep
        metrics/
            .gitkeep
```

---

## Notes

- If the script cannot connect to the server, it prints a clear message and exits.  
- This project is a minimal starting example and can be extended with LiDAR, semantic camera, custom scenarios, or planning evaluation.

