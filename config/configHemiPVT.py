from config.configSession import CONF

CONF.update({
    "task": {
        "name": "hemiPVT",
        "duration": 30,  # 2 * 60,  # duration of a block, in seconds
        "blocks": 8,  # number of blocks, try to be even
        "minTime": .1,  # in seconds, min time to be considered a valid RT
        "maxTime": .5,  # over this, RT considered a lapse
        # time window after stimulus disappearance when it still counts as a key response
        "extraTime": .5,
        "warningTime": 5,  # in seconds, time before a tone plays to wake participant up TODO: make this happen 1s after x consecutive lapses
        "victoryColor": "green",
        "earlyColor": "yellow",
        "color": '#FAFAFA',
        "maxRadius": 2,  # in cm of screen width
    },
    "fixation": {
        "colorOff": "black",
        "colorOn": "white",
        "height": .1,
        "width": .2,
        "boxColor": "red",
        "errorFlash": 0.1,  # in seconds, how long to flash box if key pushed during delay
        "minDelay":  1,  # 2,  # 2,  # in seconds, minimum delay between stimuli
        "maxDelay": 2,  # 10,  # 10,  # maximum delay between stimuli
        "scoreTime": 0.5,  # in seconds, time to show final score
        "restTime": 5,
    },
    "instructions": {
        "text": "One half of the screen will be illuminated. Pay attention to that half, while keeping your gaze on the red rectangle. When a circle appears, click the F key before it disappears. If you saw it but weren't fast enough, press the key anyway.",
        "startPrompt": "Press any key to start. Press q to quit."
    },
})


print("old size is:")
print(CONF["screen"]["size"])
CONF["screen"]["size"] = CONF["screen"]["size"] if CONF["screen"]["full"] else CONF["screen"]["debugSize"]
print("new size is:")
print(CONF["screen"]["size"])

CONF["screen"]["resolution"] = CONF["screen"]["resolution"] if CONF["screen"]["full"] else CONF["screen"]["debugResolution"]
