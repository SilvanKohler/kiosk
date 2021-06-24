from _client.pcprox import pcprox
import time

Logger = None
def print(*text):
    if len(text) == 0: text = ['']
    Logger.debug(f'{__file__}: {" ".join(str(text))}')

# https://github.com/micolous/pcprox


def run(callback):
    try:
        dev = pcprox.open_pcprox(debug=False)

        # Show the device info
        print(repr(dev.get_device_info()))

        # Dump the configuration from the device.
        config = dev.get_config()
        config.print_config()

        # Disable sending keystrokes, as we want direct control
        config.bHaltKBSnd = True

        # Turn off the red LED, turn on the green LED
        config.iRedLEDState = False
        config.iGrnLEDState = True

        # Tells pcProx that the LEDs are under application control
        config.bAppCtrlsLED = True

        # Send the updated configuration to the device
        config.set_config(dev)

        # Exit configuration mode
        dev.end_config()

        # Wait half a second
        time.sleep(.5)
        # Turn off the green LED
        config.iGrnLEDState = False
        print('Waiting for a card... (red light should pulse)')
        x = 0
        last_tag = None
        last_time = 0
        while True:
            x += 1
            x %= 6
            # flash the red LED as "1-on 1-off 1-on 3-off"
            config.iRedLEDState = (x in (0, 2))
            # LED control is in page 2, so we can explicitly only configure this
            # page.
            config.set_config(dev, [2])
            dev.end_config()
            tag = dev.get_tag()

            if tag is not None and (last_tag != tag or time.time()-last_time > 5):
                last_tag = tag
                last_time = time.time()
                # We got a card!
                # Turn off the red LED
                config.iRedLEDState = False
                config.set_config(dev, [2])
                dev.end_config()

                # Print the tag ID on screen
                bid = int(''.join(['%02x' % c for c in tag[0]]), 16)
                # print(bid)
                callback(bid)
                for x in range(20):
                    config.iGrnLEDState = x & 0x01 == 0
                    config.iRedLEDState = x & 0x02 > 0
                    config.set_config(dev, [2])
                    dev.end_config()
                    time.sleep(.1)

            # No card in the field, sleep
            time.sleep(.2)
    except KeyboardInterrupt:
        # Re-enable sending keystrokes
        config.bHaltKBSnd = True

        # Place the LEDs back under pcProx control
        config.iRedLEDState = config.iGrnLEDState = config.bAppCtrlsLED = False

        # Send the updated configuration
        config.set_config(dev)
        dev.end_config()

        dev.close()
