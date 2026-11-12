# ESP32 Water Quality Tester

A low-cost water quality monitor built on an ESP32. It measures **water temperature** (DS18B20) and **TDS** (total dissolved solids, in ppm), corrects the TDS reading for temperature, and prints the results to the Serial Monitor. Turbidity, pH and wireless logging are planned.

Written in C++ (Arduino framework) and built with PlatformIO in VS Code.

## Status

- [x] Toolchain, driver and upload working (blink test)
- [ ] DS18B20 temperature sensor reading correctly
- [ ] TDS sensor reading with temperature compensation
- [ ] TDS calibration against a known solution
- [ ] Turbidity sensor
- [ ] pH sensor
- [ ] Wi-Fi / MQTT / data logging

## Hardware

| Part | Notes |
|---|---|
| ESP32 DevKit (30-pin, ESP32-WROOM-32, CP2102 USB chip) | 3.3 V logic. Board: `esp32dev` |
| DS18B20 waterproof temperature probe | 1-Wire, 3 wires (red, black, yellow) |
| Analog TDS sensor module + probe | Input 3.3-5.5 V, output 0-2.3 V |
| 4.7 kΩ resistor (1/4 W) | Pull-up for the DS18B20 data line |
| Full-size breadboard + jumper wires | |
| Micro-USB **data** cable | Charge-only cables will not work |

Planned: turbidity sensor (5 V, needs a 10 kΩ / 20 kΩ voltage divider on its signal), pH module, calibration solutions.

## Wiring

```
ESP32 3V3 ──┬── DS18B20 red
            │
          [4.7k]
            │
ESP32 D4 ───┴── DS18B20 yellow (data)

ESP32 GND ───── DS18B20 black

ESP32 3V3 ───── TDS module VCC (+)
ESP32 GND ───── TDS module GND (-)
ESP32 D34 ───── TDS module signal (A)
```

| Signal | ESP32 pin |
|---|---|
| DS18B20 data | GPIO 4 |
| TDS analog out | GPIO 34 (ADC1, input only) |
| Turbidity (planned) | GPIO 35 via voltage divider |

**Rules**

- Never put 5 V on a GPIO pin. The ESP32 is 3.3 V only.
- Use ADC1 pins (GPIO 32-39) for analog sensors, since ADC2 stops working when Wi-Fi is on.
- Wire with the USB unplugged.
- Keep the breadboard and electronics dry. Only the probe tips go in the water.

## Software setup

1. Install [VS Code](https://code.visualstudio.com/) and the **PlatformIO IDE** extension.
2. If the board does not show up as a COM port, install the **CP210x USB driver** from Silicon Labs.
3. Open this folder (the one containing `platformio.ini`) in VS Code.
4. `platformio.ini`:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
lib_deps =
    paulstoffregen/OneWire
    milesburton/DallasTemperature
```

5. Build (✓), upload (→), then open the Serial Monitor (plug icon). If the upload stalls at `Connecting...`, hold the **BOOT** button until it starts.
6. Close the Serial Monitor before uploading again, since it holds the COM port.

## How the code works

`src/main.cpp`:

- **Non-blocking timing.** Uses `millis()` instead of `delay()`, so the TDS sensor is sampled while the temperature sensor is converting.
- **TDS sampling.** One sample every 40 ms, 30 samples per reading. The **median** is used, which ignores noise spikes better than an average.
- **Temperature reading.** The DS18B20 is asked for a temperature every 2 s. The result is read about 800 ms later.
- **Temperature compensation.** Conductivity rises about 2 % per °C above 25 °C, so the voltage is corrected first:

```
coeff = 1.0 + 0.02 * (tempC - 25.0)
v     = volts / coeff
TDS   = (133.42*v^3 - 255.86*v^2 + 857.39*v) * 0.5   [ppm]
```

The polynomial is the commonly used DFRobot curve for this style of module. Treat results as approximate until calibrated.

### Example output

```
Temp: 28.5 C | TDS voltage: 0.512 V | TDS: 245 ppm
```

## Calibration

Set `TDS_CAL_FACTOR` at the top of `main.cpp` to `known_value / measured_value`, using a reference solution (for example 342 ppm) or a trusted TDS pen. The default is `1.0`.

Rough sanity checks: probe in air reads about 0 ppm; distilled water reads close to 0-30 ppm; tap water usually reads a few hundred ppm.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `-127.00` temperature | DS18B20 not detected. Check the 4.7 kΩ resistor (D4 row to 3V3 row), the data wire on D4, and loose joints |
| `85.00` temperature | Sensor detected but power is unstable. Check 3V3 and GND connections |
| Garbled characters in monitor | Baud mismatch. Keep `monitor_speed = 115200` and `Serial.begin(115200)` |
| "Please specify upload_port" | No COM port. Check the data cable and the CP210x driver |
| Upload hangs at `Connecting...` | Hold BOOT during upload |
| Upload fails with port busy | Close the Serial Monitor first |
| TDS stuck at 0 | Check signal wire on GPIO 34 and that the probe connector is seated |

## Project layout

```
water-tester/
├── platformio.ini
├── README.md
└── src/
    └── main.cpp
```

## Roadmap

1. Verify DS18B20 and TDS readings, then calibrate.
2. Add the turbidity sensor (5 V power, 10 kΩ / 20 kΩ divider on the signal).
3. Add a pH module with buffer-solution calibration.
4. Send readings over Wi-Fi (MQTT or HTTP) and log to a dashboard.
5. Build a waterproof enclosure and battery power.

## Acknowledgements

TDS conversion constants follow the DFRobot Gravity Analog TDS sensor documentation. Uses the OneWire and DallasTemperature libraries.
