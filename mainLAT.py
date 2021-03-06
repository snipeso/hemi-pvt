import logging
import os
import random
import time
import datetime
import sys
# import psychtoolbox as ptb

from chronometer import Chronometer
from screen import Screen
from scorer import Scorer
from trigger import Trigger
from psychopy import core, event, sound
from psychopy.hardware import keyboard
from pupil_labs import PupilCore

from datalog import Datalog
from config.configLAT import CONF

#########################################################################

######################################
# Initialize screen, logger and inputs

logging.basicConfig(
    level=CONF["loggingLevel"],
    format='%(asctime)s-%(levelname)s-%(message)s',
)  # This is a log for debugging the script, and prints messages to the terminal


# needs to be first, so that if it doesn't succeed, it doesn't freeze everything
eyetracker = PupilCore(ip=CONF["pupillometry"]
                       ["ip"], port=CONF["pupillometry"]["port"], shouldRecord=CONF["recordEyetracking"], shouldSave=CONF["savePupillometry"])

trigger = Trigger(CONF["trigger"]["serial_device"],
                  CONF["sendTriggers"], CONF["trigger"]["labels"])

screen = Screen(CONF)

scorer = Scorer()

datalog = Datalog(OUTPUT_FOLDER=os.path.join(
    'output', CONF["participant"] + "_" + CONF["session"]), CONF=CONF)  # This is for saving data TODO: apply everywhere

kb = keyboard.Keyboard()

mainClock = core.MonotonicClock()  # starts clock for timestamping events

alarm = sound.Sound(os.path.join('sounds', CONF["instructions"]["alarm"]),
                    stereo=True)

questionnaireReminder = sound.Sound(os.path.join(
    'sounds', CONF["instructions"]["questionnaireReminder"]), stereo=True)


logging.info('Initialization completed')

#########################################################################


def quitExperimentIf(toQuit):
    "Quit experiment if condition is met"

    if toQuit:
        scorer.getScore()
        logging.info('quit experiment')
        trigger.send("Quit")
        trigger.reset()
        eyetracker.stop_recording()
        sys.exit(2)


def onFlip():
    "Send and restart clocks as soon as screen changes"
    trigger.send("Stim")
    kb.clock.reset()
    datalog["startTime"] = mainClock.getTime()


##############
# Introduction
##############

# Display overview of session
screen.show_overview()
core.wait(CONF["timing"]["overview"])

# Optionally, display instructions
if CONF["showInstructions"]:
    screen.show_instructions()
    key = event.waitKeys()
    quitExperimentIf(key[0] == 'q')

# start recording and set destination folder
eyetracker.start_recording(os.path.join(
    CONF["participant"], CONF["task"]["name"], CONF["session"]))

# Blank screen for initial rest
screen.show_blank()
logging.info('Starting blank period')

trigger.send("StartBlank")
core.wait(CONF["timing"]["rest"])
trigger.send("EndBlank")

# Cue start of the experiment
screen.show_cue("START")
trigger.send("Start")
core.wait(CONF["timing"]["cue"])

##########################################################################


#################
# Main experiment
#################

# initialize variables
stimulus_number = 0
tone_number = 0
totBlocks = CONF["task"]["blocks"]

# Experiment conditions
showLeft = random.choice([True, False])


################################################
# loop through blocks, switching side every time
for block in range(1, totBlocks + 1):

    # set counter
    totMissed = 0

    # set hemifield
    showLeft = not showLeft  # switches visual field
    screen.set_background(showLeft)

    if showLeft:
        trigger.send("StartBlockLeft")
    else:
        trigger.send("StartBlockRight")

    logging.info(f"{block} / {totBlocks}")

    # start block
    blockTimer = core.CountdownTimer(CONF["task"]["duration"])
    while blockTimer.getTime() > 0:
        stimulus_number += 1
        datalog["trialID"] = trigger.sendTriggerId()
        eyetracker.send_trigger(
            "StartTrial", {"id": stimulus_number, "block": block, "showLeft": showLeft})
        logging.info('Starting iteration #%s with leftOn=#%s',
                     stimulus_number, showLeft)

        ###############################
        # Wait a random period of time

        # create delay for wait
        delay = random.uniform(
            CONF["fixation"]["minDelay"],
            CONF["fixation"]["maxDelay"]) - CONF["task"]["extraTime"]  # the extra time delay happens after stimulus presentation

        logging.info('Starting delay of %s seconds', delay)

        # start delay
        delayTimer = core.CountdownTimer(delay)

        extraKeys = []
        tones = []
        while delayTimer.getTime() > 0:

            # play randomly tones in the mean time
            tone = sound.Sound(os.path.join(
                "sounds", CONF["tones"]["tone"]), volume=CONF["tones"]["volume"])

            toneDelay = random.uniform(
                CONF["tones"]["minTime"], CONF["tones"]["maxTime"])

            toneTimer = core.CountdownTimer(toneDelay)
            logging.info("tone delay of %s", toneDelay)
            while delayTimer.getTime() > 0 and toneTimer.getTime() > 0:

                #  Record any extra key presses during wait
                key = kb.getKeys()
                if key:
                    quitExperimentIf(key[0].name == 'q')
                    trigger.send("BadResponse")
                    extraKeys.append(mainClock.getTime())
                    print(key[0].name)

                    # Flash the fixation box to indicate unexpected key press
                    screen.flash_fixation_box()

            # don't play sound if there's less time left than the tone's duration
            if delayTimer.getTime() < 0.05:
                continue

            # play tone on next flip TODO: see if this is ok
            nextFlip = screen.window.getFutureFlipTime(clock='ptb')

            preTonePupil = [eyetracker.getPupildiameter(), mainClock.getTime()]

            tone.play(when=nextFlip)
            trigger.send("Tone")
            eyetracker.send_trigger("Tone", {"toneNumber": tone_number})
            toneTime = mainClock.getTime()
            core.wait(CONF["tones"]["duration"])

            postTonePupil = [
                eyetracker.getPupildiameter(), mainClock.getTime()]

            # log
            logging.info("tone at %s", mainClock.getTime())
            tones.append({
                "toneNumber": tone_number,
                "time": toneTime,
                "prePupil": preTonePupil,
                "postPupil": postTonePupil
            })
            tone_number += 1

        # log data
        datalog["hemifield"] = "left" if showLeft else "right"
        datalog["block"] = block
        datalog["sequence_number"] = stimulus_number
        datalog["delay"] = delay
        datalog["tones"] = tones
        datalog["extrakeypresses"] = extraKeys
        scorer.scores["extraKeys"] += len(extraKeys)

        core.wait(CONF["task"]["extraTime"])

        #######################
        # Stimulus presentation

        # create new x and y
        coordinates = screen.generate_coordinates()
        datalog["coordinates"] = coordinates

        # initialize stopwatch
        missed = False
        late = False

        datalog["preSpotPupil"] = [
            eyetracker.getPupildiameter(), mainClock.getTime()]  # TODO: make dict
        eyetracker.send_trigger(
            "Stim", {"sequence_number": stimulus_number, "coordinates": coordinates})

        # run stopwatch
        logging.info("waiting for shrinking to start")
        timer = core.CountdownTimer(CONF["task"]["maxTime"])
        screen.window.callOnFlip(onFlip)

        screen.start_spot()
        keys = []

        while not keys:
            keys = kb.getKeys(waitRelease=False)
            now = timer.getTime()
            if keys:
                trigger.send("Response")
            if now <= -CONF["task"]["extraTime"]:  # stop waiting for keys
                missed = True
                break
            elif now <= 0:  # keep waiting for keys, but don't show stimulus
                late = True
                radiusPercent = 0
            else:  # shrink stimulus
                radiusPercent = now/CONF["task"]["maxTime"]

            screen.shrink_spot(radiusPercent)

        datalog["postSpotPupil"] = [
            eyetracker.getPupildiameter(), mainClock.getTime()]
        #########
        # Outcome

        if missed:
            logging.info("missed")
            datalog["missed"] = True
            scorer.scores["missed"] += 1
            totMissed += 1

            # raise alarm if too many stimuli missed
            logging.warning("Missed: %s", totMissed)
            if totMissed >= CONF["task"]["maxMissed"]:
                trigger.send("ALARM")
                alarm.play()
                datalog["alarm"] = mainClock.getTime()
                eyetracker.send_trigger("Alarm")
                logging.warning("alarm sound!!!!!")

        else:
            reactionTime = keys[0].rt
            eyetracker.send_trigger(
                "Response", {"late": late, "RT": reactionTime})

            logging.info('RT: %s', reactionTime)

            # show result
            screen.show_result(reactionTime)
            core.wait(CONF["fixation"]["scoreTime"])
            screen.show_background()

            # exit if asked
            quitExperimentIf(keys[0].name == 'q')

            # reset missed count
            totMissed = 0

            # save to memory
            datalog["rt"] = reactionTime
            datalog["response_key"] = keys[0].name

            if reactionTime > CONF["task"]["minTime"]:
                scorer.newRT(reactionTime)
                if late:
                    datalog["late"] = True
                    scorer.scores["late"] += 1

        # save data to file
        datalog.flush()

    # Brief blank period to rest eyes and signal block change
    screen.show_cue(f"{block} / {totBlocks}", )
    logging.info('Starting block switch rest period')
    core.wait(CONF["fixation"]["restTime"])

###########
# Concluion

# End main experiment
screen.show_cue("DONE!")
trigger.send("End")
core.wait(CONF["timing"]["cue"])

# Blank screen for final rest
screen.show_blank()
logging.info('Starting blank period')

trigger.send("StartBlank")
core.wait(CONF["timing"]["rest"])
trigger.send("EndBlank")

logging.info('Finished')
scorer.getScore()
trigger.reset()
eyetracker.stop_recording()

questionnaireReminder.play()
core.wait(2)
