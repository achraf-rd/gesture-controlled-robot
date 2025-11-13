# Hardware Setup Guide

This guide will walk you through setting up the hardware components for the gesture-controlled robot project.

## Required Components

### Electronic Components
- **ESP32 Development Board** (ESP32-DevKitC or similar)
- **Motor Driver Module** (L298N or TB6612FNG)
- **2x DC Gear Motors** (6-12V, with wheels)
- **Power Supply** (7.4V Li-Po battery or 6x AA batteries)
- **Jumper Wires** (Male-to-Male and Male-to-Female)
- **Breadboard** (optional, for prototyping)
- **Robot Chassis** (acrylic or 3D printed)

### Tools Required
- Soldering iron and solder
- Wire strippers
- Screwdriver set
- Multimeter (for testing)

## Circuit Diagram

```
ESP32 DevKit     L298N Motor Driver     DC Motors
┌─────────────┐  ┌─────────────────┐   ┌─────────┐
│             │  │                 │   │         │
│     GPIO2   ├──┤ IN1 (ML_Ctrl)   │   │  Motor  │
│     GPIO5   ├──┤ ENA (ML_PWM)    ├───┤  Left   │
│     GPIO4   ├──┤ IN3 (MR_Ctrl)   │   │         │
│     GPIO16  ├──┤ ENB (MR_PWM)    ├───┤ Motor   │
│             │  │                 │   │ Right   │
│     GND     ├──┤ GND             │   └─────────┘
│     3V3     ├──┤ 5V (Logic)      │
│             │  │                 │
└─────────────┘  │ VCC ────────────────── +7.4V (Battery)
                 │ GND ────────────────── GND (Battery)
                 └─────────────────┘
```

## Step-by-Step Assembly

### Step 1: Prepare the Chassis
1. Assemble your robot chassis according to the manufacturer's instructions
2. Mount the two DC motors to the chassis
3. Attach wheels to the motors
4. Add a caster wheel or ball bearing for stability (optional)

### Step 2: Mount the Electronics
1. Secure the ESP32 development board to the chassis using standoffs or double-sided tape
2. Mount the motor driver module nearby
3. If using a breadboard, place it in an accessible location

### Step 3: Wire the Motor Driver
1. **Power connections:**
   - Connect battery positive (+7.4V) to VCC on motor driver
   - Connect battery negative (GND) to GND on motor driver
   - Connect ESP32 GND to motor driver GND

2. **Logic power:**
   - Connect ESP32 3V3 to motor driver 5V (logic power)
   - Or use a separate 5V regulator if needed

3. **Motor connections:**
   - Connect left motor to OUT1 and OUT2 on motor driver
   - Connect right motor to OUT3 and OUT4 on motor driver

### Step 4: Connect ESP32 to Motor Driver
Wire the following connections:

| ESP32 Pin | Motor Driver Pin | Function |
|-----------|------------------|----------|
| GPIO2     | IN1              | Left motor direction |
| GPIO5     | ENA              | Left motor PWM speed |
| GPIO4     | IN3              | Right motor direction |
| GPIO16    | ENB              | Right motor PWM speed |
| GND       | GND              | Common ground |

### Step 5: Power Supply Setup
1. **Using Li-Po Battery (Recommended):**
   - Use a 7.4V (2S) Li-Po battery
   - Add a power switch between battery and motor driver
   - Include a fuse for safety (2-5A rating)

2. **Using AA Batteries:**
   - Use 6x AA batteries (9V total)
   - Add a voltage regulator if voltage is too high

### Step 6: Safety Considerations
1. **Fuse Protection:** Add a 3-5A fuse in the positive power line
2. **Power Switch:** Include an easily accessible power switch
3. **Secure Wiring:** Use cable ties to secure all wiring
4. **Test Continuity:** Use a multimeter to verify all connections

## Testing the Hardware

### Initial Power Test
1. Connect power with motors disconnected
2. Verify ESP32 receives power (LED indicators)
3. Check voltage levels with multimeter:
   - Motor driver VCC: Should match battery voltage
   - ESP32 3V3: Should be ~3.3V
   - Logic pins: Should be 0V when no signal

### Motor Test
1. Connect motors to driver
2. Upload basic test code to ESP32
3. Verify each motor spins in both directions
4. Check that PWM speed control works

### Communication Test
1. Connect ESP32 to WiFi network
2. Test UDP communication with Python script
3. Verify commands are received and executed

## Troubleshooting

### Power Issues
- **ESP32 doesn't boot:** Check power connections, ensure sufficient voltage
- **Motors don't spin:** Verify motor driver power, check wiring
- **Erratic behavior:** Add decoupling capacitors near ESP32

### Communication Issues
- **WiFi connection fails:** Check credentials, signal strength
- **Commands not received:** Verify IP address, port settings
- **Delayed response:** Check network latency, reduce command frequency

### Mechanical Issues
- **Robot doesn't move straight:** Adjust wheel alignment, balance weight distribution
- **Insufficient torque:** Use lower gear ratio motors, increase voltage
- **Excessive vibration:** Secure all components, balance the chassis

## Wiring Diagram

```
                     ESP32 DevKit
                   ┌─────────────────┐
                   │                 │
            3V3 ───┤ 3V3         GND ├─── GND
                   │                 │
        ML_Ctrl ───┤ GPIO2           │
        ML_PWM  ───┤ GPIO5           │
        MR_Ctrl ───┤ GPIO4           │
        MR_PWM  ───┤ GPIO16          │
                   │                 │
                   └─────────────────┘
                            │
                            │
                     L298N Driver
                   ┌─────────────────┐
                   │                 │
            3V3 ───┤ 5V          VCC ├─── +7.4V
            GND ───┤ GND         GND ├─── GND
                   │                 │
        ML_Ctrl ───┤ IN1        OUT1 ├─── Motor Left +
        ML_PWM  ───┤ ENA        OUT2 ├─── Motor Left -
        MR_Ctrl ───┤ IN3        OUT3 ├─── Motor Right +
        MR_PWM  ───┤ ENB        OUT4 ├─── Motor Right -
                   │                 │
                   └─────────────────┘
```

## Final Assembly Tips

1. **Cable Management:** Use cable ties and heat shrink tubing for clean wiring
2. **Access Ports:** Leave access for USB programming and power switch
3. **Weight Distribution:** Balance components to prevent tipping
4. **Expansion:** Leave space for additional sensors or components
5. **Documentation:** Take photos of wiring before closing the chassis

## Next Steps

After completing the hardware setup:
1. Flash the ESP32 firmware from `esp32/robot_controller/`
2. Test basic movement commands
3. Set up the Python environment on your computer
4. Run the gesture control application
5. Calibrate the gesture recognition zones

For software setup instructions, see the main [README.md](../README.md) file.