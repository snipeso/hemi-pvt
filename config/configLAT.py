from config.updateConfig import UpdateConfig

latCONF = {
    "task": {
        "name": "LAT",
        # duration of a block, in seconds
        "duration": {"versionMain": 2*60, "versionDemo": 30, "versionDebug": 20},
        # number of blocks, try to be even
        "blocks": {"versionMain": 6, "versionDemo": 2, "versionDebug": 2},
        "minTime": .1,  # in seconds, min time to be considered a valid RT
        "maxTime": .5,  # over this, RT considered a lapse
        # time window after stimulus disappearance when it still counts as a key response
        "extraTime": .5,
        "victoryColor": "green",
        "earlyColor": "yellow",
        "color": '#F7F7F7',
        "maxRadius": 1,  # in cm of screen width
        "maxMissed": 5
    },
    "fixation": {
        "colorOff": "black",
        "colorOn": "white",
        "height": 1,
        "width": 2,
        "boxColor": "red",
        "errorFlash": 0.1,  # in seconds, how long to flash box if key pushed during delay
        "minDelay":  2,  # 1   # in seconds, minimum delay between stimuli. these values compensate for other delays introduced in the process
        "maxDelay": 10,  # 10,  # 10,  # maximum delay between stimuli
        "scoreTime": 0.5,  # in seconds, time to show final score
        "restTime": 3,
    },
    "instructions": {
        "text": "One half of the screen will be illuminated. Pay attention to that half, while keeping your gaze on the red rectangle. When a circle appears, click the shift key before it disappears. If you saw it but weren't fast enough, press the key anyway. Little noise bursts will be presented throughout. Do NOT push any button in response to sounds.",
        "startPrompt": "Press any key to start. Press q to quit.",
        "alarm": "horn.wav",
        "questionnaireReminder": "answerQuestionnaire.wav"
    },
    "tones": {
        "minTime": 1.5,
        "maxTime": 5,
        "tone": "Pink50ms.wav",
        "volume": 0.3,  # TODO
        "duration": 0.05,
    }
}

latTriggers = {
    "StartBlockLeft": 10,
    "StartBlockRight": 11,
    "Tone": 12,
}

updateCofig = UpdateConfig()
updateCofig.addContent(latCONF)
updateCofig.addTriggers(latTriggers)

CONF = updateCofig.getConfig()
