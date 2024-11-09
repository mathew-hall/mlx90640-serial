# Basic thermal camera based on MLX90640

Usage: Run `python3 cam.py` with the device connected via a standard serial dongle.

If you have multiple serial devices connected, then the script will need modifying to select the appropriate device, otherwise it will use the only connected device.

Derived from these projects:

* [eawariyah's GUI](https://github.com/eawariyah/SparkFun_MLX90640_Arduino_Example)
* [sipeed's serial protocol implementation](https://github.com/sipeed/MaixPy-v1_scripts/blob/master/modules/others/mlx90640/mlx90640.py)