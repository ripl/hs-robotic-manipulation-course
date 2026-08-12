# Motor Setup and Control

This module covers Dynamixel Wizard setup, motor IDs, manual position control, and recording board positions.

## Dynamixel Wizard Scan Settings

1. Open Dynamixel Wizard 2.0.
2. In the scan options, use motor IDs `0` to `15`.
3. Enable Protocol 2.0.
4. Scan the USB port connected to the robot.
5. Use baud rates `57600` and `1000000`.
6. Scan one arm at a time.

The follower arm uses IDs `1` through `6`. The leader arm uses IDs `7` through `12`.

## Configure the Device Name

Before running robot scripts, set the USB device name in `robotics/config.json`.

Example:

```json
{
  "device_name": "/dev/ttyACM2"
}
```

The exact device name depends on the laptop and USB port.

## Run Position Control

From the repository root:

```bash
source env/bin/activate
python robotics/position_control.py -l
```

Use small deltas when first moving the arm. Large moves can crash the arm into the table or over-rotate a joint.

## Record Positions

The recording script stores positions for named actions:

```bash
python robotics/record_positions.py -l
```

Press Enter to record each position.

## Joint Direction Notes

| Motor | Joint | Positive direction | Negative direction |
| --- | --- | --- | --- |
| 1 | Base | Left | Right |
| 2 | Base | Forward | Back |
| 3 | Elbow | Up | Down |
| 4 | Wrist | Up | Down |
| 5 | Wrist | Right | Left |
| 6 | Claw | Open | Close |

Follower arm home position:

```text
2048, 1800, 1850, 1100, 2048, 2048
```

## If a Motor Stops Working

- Open Dynamixel Wizard.
- Check whether the motor has an overload warning.
- If it does, reboot the motor.
- Check for tangled wires or overheating.
- Give an overheated motor time to cool before continuing.

Motor 5 is especially prone to overheating and wire tangling.
