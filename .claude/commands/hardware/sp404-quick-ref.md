# SP-404MK2 Quick Reference

Quick reference for button combinations, shortcuts, parameters, and specifications.

## Table of Contents
- Parameter guide (SYSTEM, PAD SETTING, EFX SETTING, MFX List)
- List of shortcut keys
- Error messages
- Audio diagram
- Main specifications
- MIDI implementation chart

---

Appendix
Parameter guide

## System


## General

Parameter
Value
Explanation
Edit Knob Mode
This sets how the values change when you move the knobs.
Catch
When you move a knob, control data is only outputted when the position of the knob
reaches or “catches up” to the value of its internal parameter.
* In “Mixing the samples (DJ MODE) (p. 85)”, the knobs work in Catch mode,
regardless of the settings.
Direct
When you move a knob, the control data (current position) is always outputted.
EFX Knob Mode
This sets how the values change when you move the knobs.
Catch
When you move a knob, control data is only outputted when the position of the knob
reaches or “catches up” to the value of its internal parameter.
Direct
When you move a knob, the control data (current position) is always outputted.
Manual
When you switch effects, control data corresponding to the position of the knob is
outputted.
Load Project
This sets the project that loads when the unit starts up.
Last
Loads the project that was used right before the power was last turned off.
1–16
Loads a specified project.
Sub Pad Mode
This sets the functionality of the [SUB PAD] button in sample mode.
Retrig
Retriggers the current pad (plays its sound again).
SkipBack
Switches to skip-back mode.
Auto Trig Level
1–10
Sets the level at which note input is detected (the level at which sampling
automatically starts, and the level at which recording to the skip-back memory
begins).
Scrn Saver Time
1, 5, 10 (min)
Sets the time before the screen saver starts (in minutes).
* The pads for which samples are not set (blank pads) do not light up while the
screen saver is shown.
Scrn Saver Type
OldRave, Naminori
Selects the type of screen saver.
Custom
When you select “Custom”, you can use an image file that you’ve imported as the
screen image for the screen saver (Customizing the screen saver (p. 99)).
Disp Off
Select “Disp Off” to turn off the display.
BPM Auto Dtct

## Off, On

When this is set to “ON”, the tempo (BPM) is automatically detected when you import
a sample.
BPM Detect Rng
100-199, 80-159, 70-139,
50-99
Selects the range at which the tempo (BPM) of a sample is automatically detected.
Pad MUTE
When Pad MUTE is on, this selects whether to monitor the muted samples.
Mst+Phn
Muted samples are not outputted to any jack.
Master
Muted samples can be output (monitored) from the PHONES jack. In this case, no
effects are applied.
Appendix
Parameter
Value
Explanation
PTN Change Mode
This sets how the samples play back when switching between patterns during pattern playback.

## Mkii

Sample playback stops when the pattern changes.

## Sx

Sample playback continues when the pattern changes.
Pop-up Time
Normal, Short, OFF
Sets how long the popup screens are displayed.
Set this to “Short” to make the popup screens display for a shorter time than the
“Normal” setting.
Set this to “OFF” if you don’t want popups to display.
MARK Function
This sets the function to be recalled when you press the [MARK] button.
SBS Def
Recalls the skip-back sampling function (with a maximum recording time of 25
seconds).
SBS Long
Recalls the skip-back sampling function (with a maximum recording time of 40
seconds).
Looper
Recalls the looper function.
Reverse Type
This selects the point (time) at which reverse playback begins when you press the [REVERSE] button during sample
playback.
Starts reverse playback at the sample’s end point. This works the same as the

## Sp-404Sx.

Starts reverse playback immediately from the playback position of the current sample.
This works the same as the SP-303.

## Usb In

This selects where the audio signal input from the USB port is sent.

## Line In

Mixes the USB audio signal with the audio signal from the LINE IN jacks.

## Mix Out

Mixes the USB audio signal with the MIXER output, without going through the INPUT
FX or BUS FX.
DJ Mode TS type
This lets you change how the audio is processed when changing the playback speed of a sample in DJ mode.

## Vinyl

Changes the playback speed and pitch at the same time, like an analog record.

## Backing

Independently controls the playback speed and pitch.
Processes the sound as appropriate for musical instruments whose sounds have a
noticeable decay.

## Ensemble

Independently controls the playback speed and pitch.
Processes the sound as appropriate for musical instruments that have a sustaining
sound.
Bend Sens (DJ)
10–200
Sets how quickly the pitch of a sample changes when you press the [BEND-] and
[BEND+] pads.
FileSystem
Selects the character code for filenames that can be recognized by this unit when you import a sample.
The unit must be restarted once you’ve changed the settings and pressed the [EXIT] button to exit the SYSTEM
screen.
Multi-Byte
Letters, numbers, symbols, double-byte characters (kanji, hiragana, katakana)
This lets the unit recognize and import files with filename that use double-byte and
similar characters. Note that this unit doesn’t correctly display double-byte characters,
and these characters appear garbled.
Latin1
Letters, numbers, symbols
With this setting, files with double-byte characters in their filenames can’t be
recognized by this unit.
Bank Mute

## Off, On

When this is ON, the sound is automatically muted when a sample in another bank is
playing.
App Auto Connection

## Off, On

When this is ON, the unit automatically connects when you launch a third-party app
(such as Serato DJ, Koala Sampler, Melodics, etc.).
Start-up Screen
Default, Skip
If this is set to Skip, some of the startup screens are skipped.
Appendix

## Click

Parameter
Value
Explanation
Output Assign

## Off, On

When this is set to ON, the metronome sound is output from the LINE OUT jacks and
from the USB port.
Click Level
1–5
Sets the volume of the metronome.
Metronome:REC

## Off, On

When this is ON, the metronome sound is output while you are sampling or
resampling.
Metronome:PTN

## Off, On

When this is ON, the metronome sound is output when a pattern is being recorded.
Count-In:REC
This selects how sampling or resampling starts.

## Off

Sampling or resampling starts at the same time that you press the [REC] button.

## 1 Meas, 2 Meas

When you press the [REC] button, a count-in begins one or two measures before
where sampling or resampling begins.

## Wait

Sampling or resampling starts when you press a pad to play back a sample, or when
audio is detected from an external device.
Count-In:PTN
This selects how pattern recording begins.

## Off

Pattern recording starts at the same time that you press the [REC] button.

## 1 Meas, 2 Meas

When you press the [REC] button, a count-in of one or two measures begins before
pattern recording starts.

## Wait

Pattern recording starts when you press a pad to play back a sample, or when audio is
detected from an external device.

## Midi

Parameter
Value
Explanation
MIDI Sync
Specifies the tempo source.
Auto
The tempo automatically synchronizes to the MIDI clocks if MIDI clocks are input via
the MIDI IN connector or the USB port.
Internal
The tempo specified on this unit is used.

## Midi

The tempo synchronizes to the MIDI clocks received via the MIDI IN connector.

## Usb

The tempo synchronizes to the MIDI clocks received via the USB port.
MIDI Sync Out

## Off, On

When this is ON, clocks, start and stop are transmitted to the device connected to this
unit’s MIDI OUT connector.
SEQ Note Out

## Off, On

When this is set to “ON”, the note number corresponding to the pattern (pad) is
output via the MIDI OUT connector when the pattern plays back.
SYNC Delay
0–20ms
Adjust this if there is a delay (latency) in sound between your external MIDI device and
this unit.
Larger values make this unit play back at a more delayed timing.
When this is set to “0”, this unit plays and outputs MIDI messages with the same
timing.
Appendix
Parameter
Value
Explanation
Bend SYNC(DJ)
This sets how the MIDI clock output from this unit changes when you press the [BEND-] or [BEND+] pads to change
the playback speed of this unit.

## Off

MIDI clocks are output at a fixed rate.

## On

MIDI clocks outputted from this unit are synchronized with this unit’s playback speed.
With this setting, the tempo of MIDI devices connected externally changes in time
with the playback speed of this unit.
* If you press the [BEND-] [BEND+] pads while holding down the [REMAIN] button,
the MIDI clocks do not change (the effect is the same as the OFF setting).
PAD Note Out

## Off, On

When this is set to “ON”, note numbers corresponding to the pads are output via the
MIDI OUT connector when you play the pads.
Soft Through

## Off, On

If this is “ON”, MIDI messages that are input to the MIDI IN connector are output to the
MIDI OUT connector.
USB-MIDI Thru

## Off, On

When this is “ON”, MIDI signals that are input via the USB port are output to the MIDI
OUT connector. MIDI signals that are inputted via the MIDI IN connector are also
outputted to the USB port.
The inputted MIDI signals are also transmitted to the internal sound module at that
time.
PC Rx

## On, Off

When this is ON, program change messages are received.
MIDI Mode

## A, B

Changes the note number assignment according to the mode you’ve selected.
For details, refer to “MIDI note map (p. 154)”.
Pad MIDI Channels
1/2, 2/3–9/10, 10/11
Sets the offset value for the MIDI channel.
This setting is enabled when “MIDI Mode” is set to “B”.
Note offset
-11–35
Sets the offset value for the note number.
This setting is enabled when “MIDI Mode” is set to “B”.

## Midi Ext Src

This selects how the [EXT SOURCE] button is triggered when notes are received via an external MIDI source.

## Toggle

A note-on message toggles the [EXT SOURCE] button on/off.

## Gate

A note-on message turns the [EXT SOURCE] button on, and a note-off message turns
the [EXT SOURCE] button off.

## Through

The [EXT SOURCE] button is not affected by external MIDI note data.

## Gain

Parameter
Value
Explanation
Attenuator

## Off, On

When this is ON, the gain of the audio input from the LINE IN jacks is lowered.
Turn the Attenuator on when the LINE IN input seems to be distorting.
Noise Gate
Reduces the noise floor in the signal input from the LINE IN and INPUT jacks.

## Off

The noise gate is not used.
-9dB, -12dB, -18dB
Reduces the noise floor at the specified level.
-Inf
Reduces the noise floor to the bare minimum.

## Line Out

0, +6, +12 (dB)
Sets the gain of the audio output from the LINE OUT jacks.

## Phones Out

-18, -12, -6, 0, +6, +12 (dB)
Sets the gain of the audio output from the PHONES OUT jacks.

## Usb Out

-24, -12, 0 (dB)
Sets the gain of the audio output from the USB port.
Appendix
Parameter
Value
Explanation
Anti Feedback

## Off, On

When this is “ON”, the anti-feedback function is enabled for the mic input.
This helps prevent mic feedback.

## Version

Displays the version of this unit.

## Pad Setting


## Trigger

Parameter
Value
Explanation
Curve Type
Sets how the volume changes according to how hard you strike a pad.
Lin
This is the standard setting. This produces the most natural balance between playing
dynamics and volume change.
Exp
Compared to “Lin”, playing strongly produces a greater change in volume.
Log
Compared to “Lin”, playing softly produces a greater change in volume.
Fix
Sets the volume at a fixed level of 127.
Threshold
1–100
This sets the minimum sensitivity of the pads, at which the trigger signal is received only
when a pad is struck with at least a certain amount of force (velocity). This can be used to
prevent a pad from sounding due to vibrations from other pads.
Gain
0–100
The sensitivity is adjusted with the curve as-is. The larger the value, the greater the sensitivity
is when playing the pads.
Trig Span
1–10
Adjusts the sensitivity of the pads to repeated strikes. With lower values, the pads detect
repeated strikes within a shorter time interval. Set this value higher if you don’t want the pad
to accidentally detect repeated strikes.

## Led

Parameter
Value
Explanation
LED Brightness
1–10
Sets the brightness of the indicators on the buttons and pads. This sets the brightness when
the buttons or pads are highlighted.
LED Glow
1–10
Sets the brightness of the indicators on the buttons and pads. This sets the brightness when
the buttons or pads are not highlighted.
Appendix
Parameter
Value
Explanation
Pad LED Mode
This selects the color of the pad illumination.

## Bus

Pad Color <BUS>
The pads light up in the color set in “BUS COLOR”.
In this mode, the pad colors change according to the bus through which the sample audio is
sent.

## Pad

Pad Color <PAD>
The pads light up in the color set in “PAD COLOR”.
In this mode, the pad colors are set for individual pads (up to 16).

## Sample

Pad Color <SAMPLE>
In this mode, the pad colors are set for individual samples (up to 2,560).
For details, refer to “Setting the pad colors for each sample (Pad Color <SAMPLE>) (p. 53)”.

## Bus Color

Parameter
Value
Explanation
BUS1 Color
Default, 1–127, White
Changes the pad color for each bus through which sample audio is sent.
This can be set for BUS 1, BUS 2 and DRY respectively.
This is enabled when Pad LED Mode is “BUS”.
* Hold down the [SHIFT] button and turn the [VALUE] knob to change the value in
steps of 10.
BUS2 Color
DRY Color

## Pad Color

Parameter
Value
Explanation

## Pad-1–Pad-16

Default, 1–127, White
Specifies the colors of individual pads.
This is enabled when Pad LED Mode is “PAD”, and when a sample is either playing
back or stopped while in sample mode.

## Efx Setting


## Favorite

Appendix
Parameter
Value
Explanation
Routing

## Type A, Type B

Selects the routing (connection) of the bus to which effects are assigned.
“Configuring the effect routing (p. 104)”

## Favorite

Bypass, 1–16
Selects the combination of effects assigned to BUS 3 and BUS 4.
“Changing the effects assigned to BUS 3 and BUS 4 (p. 105)”

## Bus 3, Bus 4

Parameter
Value
Explanation
EFX Type
Bypass, 303 VinylSim, 404 VinylSim, Cassette Sim, Lo-fi, Downer, Compressor,
Equalizer, Isolator, Super Filter, Filter+Drive, WrmSaturator, Overdrive,
Distortion, Crusher, Ring Mod, SBF, Resonator, Hyper-Reso, Chromatic PS,
Reverb, Ha-Dou, Zan-Zou, Sync Delay, TimeCtrlDly, Ko-Da-Ma, Tape Echo,
Chorus, JUNO Chorus, Flanger, Phaser, Wah, Slicer, Tremolo/Pan, To-Gu-Ro,
DJFX Looper, Scatter, SX Reverb, SX Delay, Cloud Delay
Selects the effects assigned to BUS
3 or BUS 4.
For details on the parameters of
each effect, refer to “MFX List (p.
128)”.

## Direct

Parameter
Value
Explanation
Direct FX1–Direct FX5
Filter+Drive, Resonator, Sync Delay, Isolator, DJFX Looper, Scatter, Downer, Ha-
Dou, Ko-Da-Ma, Zan-Zou, To-Gu-Ro, SBF, Stopper, Tape Echo, TimeCtrlDly,
Super Filter, WrmSaturator, 303 VinylSim, 404 VinylSim, Cassette Sim, Lo-fi,
Reverb, Chorus, JUNO Chorus, Flanger, Phaser, Wah, Slicer, Tremolo/Pan,
Chromatic PS, Hyper-Reso, Ring Mod, Crusher, Overdrive, Distortion, Equalizer,
Compressor, SX Reverb, SX Delay, Cloud Delay, Back Spin
You can assign the effects you like
to the effect buttons on the top
panel.
For details on the parameters of
each effect, refer to “MFX List (p.
128)”.

## Other

Parameter
Value
Explanation
Mute Bus
This individually selects the bus to mute with Mute Bus.

## All

Both BUS 1 and BUS 2 are muted.

## Bus

Only the bus selected with the
[BUS FX] button is muted.
Input FX
Bypass, Auto Pitch (*), Vocoder (*), Harmony (*), Gt Amp Sim (*), Chorus, JUNO
Chorus, Reverb, TimeCtrlDly, Chromatic PS, Downer, WrmSaturator, 303
VinylSim, 404 VinylSim, Cassette Sim, Lo-fi, Equalizer, Compressor
Effects marked with an (*) are for INPUT FX only.
You can apply effects to the audio
that’s inputted to this unit.
For details on the parameters of
each effect, refer to “MFX List (p.
128)”.
Appendix
Parameter
Value
Explanation
Input Bus
You can set the bus to which the playback audio signals coming into the INPUT jack are sent (meaning which
effects are used).

## Dry

The signal is not sent to BUS 1, BUS
2 (the BUS 1 and BUS 2 effects are
not used).

## Bus1, Bus2

The signal is sent to BUS 1 or BUS
2. The effects set for BUS 1 and
BUS 2 are used.
DRY Routing
This sets the routing for audio sent to the DRY bus.

## Dry

Audio is not sent through BUS 1–
BUS 4 (no effects are applied).

## Bus3

Audio is inserted just before BUS 3.
The BUS 3 and BUS 4 effects are
applied.

## Mfx Top

Scatter, Downer, Ha-Dou, Ko-Da-Ma, Zan-Zou, To-Gu-Ro, SBF, Stopper, Tape
Echo, TimeCtrlDly, Super Filter, WrmSaturator, 303 VinylSim, 404 VinylSim,
Cassette Sim, Lo-fi, Reverb, Chorus, JUNO Chorus, Flanger, Phaser, Wah, Slicer,
Tremolo/Pan, Chromatic PS, Hyper-Reso, Ring Mod, Crusher, Overdrive,
Distortion, Equalizer, Compressor, SX Reverb, SX Delay, Cloud Delay, Back Spin
Sets the MFX that’s used when this
unit is turned on.
For details on the parameters of
each effect, refer to “MFX List (p.
128)”.
MFX List
Filter+Drive
This is a filter with overdrive.
It cuts the specified frequencies and adds distortion.
Parameter
Value
Explanation

## Cutoff

20–16000 (Hz)
Sets the cutoff frequency range in which the filter works.

## Resonance

0–100
Adjusts the filter’s resonance level.
The larger the value, the more that the frequency range set in CUTOFF is emphasized.

## Drive

0–100
Adds distortion.

## Flt Type

Sets the type of filter.

## Hpf

Cuts off the low frequencies.

## Lpf

Cuts off the high frequencies.

## Low Freq

20–16000 (Hz)
Adjusts the frequency range that’s boosted or cut by the LOW GAIN parameter.

## Low Gain

-24–24 (dB)
Adjusts the amount of boost/cut applied to the frequency range that’s set in LOW

## Freq.

Resonator
This effect uses “Karplus-Strong synthesis”, which is often used in physical modeling of sounds.
This lets you alter the sound with a maximum of six “resonators” that match different keys or chords.
Parameter
Value
Explanation

## Root


## C-1–G9

Sets the reference pitch (root note).

## Bright

0–100
Adjusts the tonal brightness.

## Feedback

0–99 (%)
Adjusts the amount of feedback for the
effect.

## Chord

Root, Oct, UpDn, P5, m3, m5, m7, m7oct, m0, m11, M3, M5, M7, M7oct,

## M9, M11

Sets the composite notes (chord) to
resonate.
Appendix
Parameter
Value
Explanation

## Panning

0–100
Sets the panning for the resonator.

## Env Mod

0–100
Larger values increase the amount of
feedback according to the input level.
Sync Delay
Gives an echo effect in sync with the tempo.
Parameter
Value
Explanation

## Time

1/32, 1/16T, 1/32D, 1/16, 1/8T, 1/16D, 1/8, 1/4T, 1/8D, 1/4, 1/2T, 1/4D, 1/2,

## 1/1T, 1/2D, 1/1

Sets the sound delay time.

## Feedback

0–99 (%)
Adjusts the amount of feedback for the effect.

## Level

0–100
Adjusts the volume of the effect sound.

## L Damp F

FLAT, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800 (Hz)
Sets the frequency range that is attenuated each
time the delay repeats.

## H Damp F

630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
12500, FLAT (Hz)
Isolator
This effect lets you cut off sounds in a specified frequency range.
Parameter
Value
Explanation

## Low

-INF, -41.87–+12 (dB)
Adjusts the amount of boost/cut in the low-frequency
range.

## Mid

-INF, -41.87–+12 (dB)
Adjusts the amount of boost/cut in the mid-frequency
range.

## High

-INF, -41.87–+12 (dB)
Adjusts the amount of boost/cut in the high-frequency
range.
DJFX Looper
This effect loops the sound in short cycles.
You can vary the playback direction and playback speed of the input sound to get a turntable-type effect.
Parameter
Value
Explanation

## Length

0.230–0.012 (sec)
Sets the length of the loop.

## Speed

-100–100
Sets the playback direction and playback speed.
The loop plays backward when this is set to a negative value, stops when this is set to
zero, and plays forward when this is set to a positive value.

## Loop Sw


## Off, On

Turn this ON while a sound is playing to make the sound play back in a loop, at a
length specified by the LENGTH parameter.
Turn this OFF to disable the loop.
Scatter
This effect swaps the sound played back by a loop in steps, altering its playback direction and gate length. This gives you the loop playback a
digital groove feeling.
Parameter
Value
Explanation

## Type

1–10
Sets the scatter type.

## Depth

10, 20, 30, 40, 50, 60, 70, 80, 90, 100
Adjusts the scatter depth.

## Scatter


## Off, On

Switches the scatter effect on/off.

## Speed


## Single, Double

Sets the scatter speed.
Appendix
Downer
Cyclically slows down the audio playback speed.
Parameter
Value
Explanation

## Depth

0–100
Sets how much the playback speed should be slowed
down.

## Rate

2/1, 1/1, 1/2, 1/4, 1/8, 1/16, 1/32
Sets the period at which the playback speed is changed.

## Filter

0–100
Attenuates the high-frequency range.

## Pitch


## Off, On

When this is turned ON, pitches that were lowered due
to the change in speed are converted to their original
pitch.

## Resonance

0–100
Adjusts the filter’s resonance level.
Increasing the value further emphasizes the effect, for a
more unusual sound.
Ha-Dou
This effect generates a wave-like sound based on the input audio.
Parameter
Value
Explanation

## Mod Depth

0–100
Adjusts the depth of the effect
sound.

## Time

0–100
Sets the length of the effect sound.

## Level

0–100
Adjusts the volume of the effect
sound.

## Low Cut

FLAT, 20, 25, 31, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800
(Hz)
Sets the frequency range at which
the effect sound is attenuated.

## High Cut

630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
12500, FLAT (Hz)

## Pre Delay

0–100 (msec)
Sets the time it takes for the effect
to sound.
Ko-Da-Ma
This creates a reverberating audio effect.
Parameter
Value
Explanation

## Time

1/32, 1/16T, 1/32D, 1/16, 1/8T, 1/16D, 1/8, 1/4T, 1/8D, 1/4, 1/2T, 1/4D, 1/2, 1/1T,

## 1/2D, 1/1

Sets how much the effect sound is
delayed.

## Feedback

0–99 (%)
Adjusts how much the effect
sound is repeated.

## Send

0–100
Adjusts the volume of sound sent
to the effect.

## L Damp F

FLAT, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800 (Hz)
Sets the frequency range that is
attenuated each time the delay
repeats.

## H Damp F

630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
12500, FLAT (Hz)

## Mode


## Single, Pan

When this is set to “SINGLE”, the
effect sound comes from the
center; and when this is set to
“PAN”, the effect sound is heard on
the left and the right.
Zan-Zou
For left and right sounds, this effect applies delay to the negative phase of the sound. This gives the lingering effect of a sonic “afterimage”.
Appendix
The effect works for stereo sound, and does not have any effect on mono sound.
Parameter
Value
Explanation

## Time

0–100 (when the SYNC parameter is OFF)
1/32, 1/16T, 1/32D, 1/16, 1/8T, 1/16D, 1/8, 1/4T, 1/8D, 1/4, 1/2T, 1/4D, 1/2, 1/1T,
1/2D, 1/1 (when the SYNC parameter is ON)
Sets the sound delay time.

## Feedback

0–99
Adjusts the amount of feedback
for the effect.

## Hf Damp

200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000,
5000, 6300, 8000, OFF (Hz)
Sets the frequency range at which
the effect sound is attenuated
(how clearly defined the
afterimage sounds).

## Level

0–100
Adjusts the volume of the effect
sound.

## Mode


## 2Tap, 3Tap, 4Tap

Sets how the effect sound lingers.

## Sync


## Off, On

When this is ON, the effect sound
synchronizes with the tempo.
To-Gu-Ro
This gives the sound an undulating effect, based on the image of a coiled-up snake.
Parameter
Value
Explanation

## Depth

0–100
Adjusts how much the playback
speed should be slowed down.

## Rate

0–100 (when the SYNC parameter is OFF)
2/1, 1/1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128 (when the SYNC parameter is ON)
Sets the period at which the
playback speed is lowered.

## Resonance

0–100
Adjusts the filter’s resonance level.
Increasing the value further
emphasizes the effect, for a more
unusual sound.

## Flt Mod

0–100
Attenuates the high-frequency
range according to the playback
speed.

## Amp Mod

0–100
Attenuates the volume according
to the playback speed.

## Sync


## Off, On

When this is ON, the effect sound
synchronizes with the tempo.

## Sbf

A sideband filter that lets specific frequency components pass through.
Parameter
Value
Explanation

## Interval

0–100
Sets the band interval. Larger values produce wider band intervals, and the
frequency of each band increases.

## Width

0–100
Sets the bandwidth. Larger values produce a narrower bandwidth, which
further isolates the specific frequency components that pass through the filter.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect
sound.

## Type


## Sbf1, Sbf2, Sbf3, Sbf4, Sbf5, Sbf6

Sets the range in which the filter works.

## Gain

-INF, -52.3–+10.0 (dB)
Adjusts the volume of the effect sound.
Appendix
Stopper
This effect lowers the sample playback speed, reproducing the sound of a turntable stopping.
Parameter
Value
Explanation

## Depth

0–100
Adjusts how much the playback speed should be slowed down.

## Rate

4/1, 2/1, 1/1, 1/2, 1/4, 1/8, 1/16,
1/32, 1/64
Sets the period at which the playback speed is changed.

## Resonance

0–100
Adjusts the filter’s resonance level.
Increasing the value further emphasizes the effect, for a more unusual sound.

## Flt Mod

0–100
Attenuates the high-frequency range according to the playback speed.

## Amp Mod

0–100
Lowers the volume according to the playback speed.
Tape Echo
This is a virtual tape echo effect that gives a realistic tape delay sound.
The effect simulates the tape echo section of a Roland RE-201 Space Echo.
Parameter
Value
Explanation

## Time

10–800 (msec)
Sets the tape speed.
Larger values make the tape speed slower, which creates a longer interval
between delay sounds.

## Feedback

0–99 (%)
Adjusts the volume of the delay repeat sound.

## Level

0–100
Adjusts the volume of the effect sound.

## Mode


## S, M, L, S+M, S+L, M+L, S+M+L

Selects the combination of playback heads to use.

## W/F Rate

0–100
Sets the speed of wow/flutter (the complex variation in pitch caused by tape
wear and rotational irregularity).

## W/F Depth

0–100
Sets the depth of wow/flutter.
TimeCtrlDly
This is a delay in which the delay time can be varied smoothly.
Parameter
Value
Explanation

## Time

0–100 (msec) (when the SYNC parameter is OFF)
1/32, 1/16T, 1/32D, 1/16, 1/8T, 1/16D, 1/8, 1/4T, 1/8D, 1/4, 1/2T, 1/4D,
1/2, 1/1T, 1/2D, 1/1 (when the SYNC parameter is ON)
Sets the sound delay time.

## Feedback

0–99 (%)
Adjusts the amount of feedback for the
effect.

## Level

0–100
Sets the volume of the effect sound.

## L Damp F

FLAT, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800 (Hz)
Sets the frequency range that is
attenuated each time the delay repeats.

## H Damp F

630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
10000, 12500, FLAT (Hz)

## Sync


## Off, On

When this is ON, the effect sound
synchronizes with the tempo.
Super Filter
This is a filter with an extremely sharp slope (attenuation characteristics). The cutoff frequency can be varied cyclically.
Parameter
Value
Explanation

## Cutoff

0–100
Sets the frequency range in which the filter works (the cutoff
frequency). Higher values increase the frequency range.
Appendix
Parameter
Value
Explanation

## Resonance

0–100
Adjusts the filter’s resonance level.
The larger the value, the more that the frequency range set in
CUTOFF is emphasized.

## Flt Type

Sets the filter type.

## Lpf

A low-pass filter. This filter lets frequencies pass through that are
higher than the frequency range set in CUTOFF.

## Bpf

A band-pass filter. This filter lets frequencies pass through that are
near the frequency range set in CUTOFF.

## Hpf

A high-pass filter. This filter lets frequencies pass through that are
higher than the frequency range set in CUTOFF.

## Depth

0–100
Sets the depth of the effect.

## Rate

0–100 (when the SYNC parameter is OFF)
2/1, 1/1D, 2/1T, 1/1, 1/2D, 1/1T, 1/2, 1/4D, 1/2T,

## 1/4, 1/8D, 1/4T, 1/8, 1/16D, 1/8T, 1/16, 1/32D,

1/16T, 1/32, 1/32T, 1/64, 1/64T (when the SYNC
parameter is ON)
Sets the cycle (period) of the effect.

## Sync


## Off, On

When this is ON, the effect sound synchronizes with the tempo.
WrmSaturator
This is a saturator effect with a characteristic warm sound.

## Note

This effect may output a very loud sound, depending on how the parameters are set. Use caution not to raise the values too much.
Parameter
Value
Explanation

## Drive

0–48 (dB)
Adjusts the strength of the distortion.
Eq LOW
-24–24 (dB)
Adjusts the amount of boost/cut for the low-frequency range.
Eq HIGH
-24–24 (dB)
Adjusts the amount of boost/cut for the high-frequency range.

## Level

0–100
Adjusts the volume of the effect sound.
303 VinylSim
This effect models the Vinyl Sim effect of the SP-303. The effect simulates the sound of an analog record playing.
Parameter
Value
Explanation

## Comp

0–100
Sets the compression feel, a unique part of the analog record’s sound.

## Noise

0–100
Adjusts the volume of the noise.

## Wow Flut

0–100
Sets the inconsistencies (wow/flutter) heard when the analog record
“rotates”.

## Level

0–100
Adjusts the volume of the effect sound.
404 VinylSim
This effect models the Vinyl Sim effect of the SP-404SX. The effect simulates the sound of an analog record playing.
Parameter
Value
Explanation

## Frequency

0–100
Sets the frequency characteristics of the playback system.

## Noise

0–100
Adjusts the volume of the noise.

## Wow Flut

0–100
Sets the inconsistencies (wow/flutter) heard when the analog record
“rotates”.
Appendix
Cassette Sim
This effect simulates the sound of a cassette tape playing.
Parameter
Value
Explanation

## Tone

0–100
Sets the tone.

## Hiss

0–100
Adjusts the volume of the noise.

## Age

0–60 (years)
Sets how many years the cassette tape has deteriorated.

## Drive

0–100
Adjusts the amount of distortion.

## Wow Flut

0–100
Sets the inconsistencies (wow/flutter) heard when the cassette tape plays
back.
Catch
0–100
Sets how much the cassette tape has stretched out.
Lo-fi
Degrades the tonal character.
Parameter
Value
Explanation

## Pre Filt

1–6
Sets the type of pre-filter (the filter that the sound
passes through before effects are applied).

## Lofi Type

1–9
Larger settings cause more tonal degradation.

## Tone

-100–100
Sets the tone. Larger settings emphasize the
high-frequency range. Smaller settings
emphasize the low-frequency range.

## Cutoff

200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500,
3150, 4000, 5000, 6300, 8000 (Hz)
Sets the frequency range in which the post-filter
(the filter that the sound passes through after
effects are applied) works.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry
(original) sound and effect sound.

## Level

0–100
Adjusts the volume of the effect sound.

## Note

This effect may output a very loud sound, depending on how the parameters are set. Use caution not to raise the values too much.
Reverb
This adds reverberation to the sound.
Parameter
Value
Explanation

## Type


## Ambi, Room, Hall1, Hall2

Sets the type of reverb.

## Time

0–100
Sets the reverb time.

## Level

0–100
Adjusts the volume of the effect sound.

## Low Cut

FLAT, 20–800 (Hz)
Sets the frequency range at which the effect sound is attenuated.

## High Cut

630–12500, FLAT (Hz)

## Pre Delay

0–100 (ms)
Sets the time before the effect sound is output.
Chorus
Adds spaciousness and richness to the sound.
Parameter
Value
Explanation

## Depth

0–100
Sets the depth of the effect sound.

## Rate

0.33–2.30 (sec)
Sets the cycle (period) of the effect sound.
Appendix
Parameter
Value
Explanation

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect sound.

## Eq Low

-15–15 (dB)
Adjusts the amount of boost/cut of the low-frequency range.

## Eq High

-15–15 (dB)
Adjusts the amount of boost/cut of the high-frequency range.

## Level

0–100
Adjusts the volume of the effect sound.
JUNO Chorus
This effect models the chorus section of the Roland JUNO-106 and JX series.
Parameter
Value
Explanation

## Mode


## Juno 1, Juno 2, Juno12, Jx-1 1, Jx-1 2

Sets the type of effect.

## Noise

0–100
Adjusts the volume of noise generated by the effect.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and
effect sound.
Flanger
This effect creates modulation like a jet airplane taking off and landing.
Parameter
Value
Explanation

## Depth

0–100
Sets the depth of the effect sound.

## Rate

0–100 (when the SYNC parameter is OFF)
4.000–0.016 (bar; when the SYNC parameter is ON)
Sets the cycle (period) of the effect sound.

## Manual

0–100
Sets the frequency range in which the effect is applied.
Smaller values reduce the flanging effect in the low end.

## Resonance

0–100
Adjusts the filter’s resonance level.
Increasing the value further emphasizes the effect, for a
more unusual sound.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original)
sound and effect sound.

## Sync


## Off, On

When this is ON, the effect sound synchronizes with the
tempo.
Phaser
This effect creates modulation by adding a phase-shifted sound.
Parameter
Value
Explanation

## Depth

0–100
Sets the depth of the effect sound.

## Rate

0–100 (when the SYNC parameter is OFF)
4.000–0.016 (bar; when the SYNC parameter is ON)
Sets the cycle (period) of the effect sound.

## Manual

0–100
Sets the frequency range in which the effect is applied.
Larger values reduce the phasing effect in the low end.

## Resonance

0–100
Adjusts the filter’s resonance level.
Increasing the value further emphasizes the effect, for a
more unusual sound.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original)
sound and effect sound.

## Sync


## Off, On

When this is ON, the effect sound synchronizes with the
tempo.
Appendix
Wah
This effect gives a wah-wah sound, by cyclically changing the tone.
Parameter
Value
Explanation

## Peak

0–100
Larger values narrow the frequency range at which the
effect is applied.

## Rate

0–100 (when the SYNC parameter is OFF)
1.000–0.010 (bar; when the SYNC parameter is ON)
Sets the cycle (period) of the effect.

## Manual

0–100
Sets the frequency range in which the effect is applied.

## Depth

0–100
Sets the depth of the effect.

## Flt Type

Sets the filter type.

## Lpf

Applies the effect over a wide frequency range.

## Bpf

Applies the effect over a narrow frequency range.

## Sync


## Off, On

When this is ON, the effect sound synchronizes with the
tempo.
Slicer
This slices the sound up into small pieces, creating the impression that a backing phrase is being played.
This slices up the sound at certain intervals into 16 parts (16 steps), breaking the sound into a rhythm that follows the sequence pattern (a pattern
used for slicing up the sound). This is effective when used with sustaining sounds.
Parameter
Value
Explanation

## Pattern

1–32
Sets the sequence pattern.

## Speed

0–100 (when the SYNC parameter is OFF)
2/1–1/64T (when the SYNC parameter is ON)
Sets the period over which the sequence pattern
repeats.

## Depth

0–100
Sets the slicing depth. Larger settings make the slicing
effect more prominent.

## Shuffle

0–100
Larger settings delay the timing of even-numbered steps
(2, 4...).

## Mode

Sets how the volume changes when the next step sounds.

## Legato

The volume is not changed between steps.

## Slash

The volume is reset to zero before the next step sounds
(at the boundary between steps).

## Sync


## Off, On

When this is ON, the effect sound synchronizes with the
tempo.
Tremolo/Pan
Cyclically varies the volume or panning.
Parameter
Value
Explanation

## Depth

0–100
Sets the depth of the effect.

## Rate

0–100 (when the SYNC parameter is OFF)
1.000–0.010 (when the SYNC parameter is ON)
Sets the cycle (period) of the effect.

## Type

Sets the type of effect.

## Tre

Cyclically changes the volume (tremolo).

## Pan

Cyclically changes the panning.
Appendix
Parameter
Value
Explanation

## Wave

Sets how the effect modulates the sound.

## Tri

Triangle wave

## Sqr

Square wave

## Sin

Sine wave

## Saw1, Saw2

Sawtooth wave

## Trp

Trapezoidal wave

## Sync


## Off, On

When this is ON, the effect sound synchronizes with the
tempo.
Chromatic PS
A two-voice pitch shifter that changes the pitch in semitone steps.
Parameter
Value
Explanation

## Pitch1, Pitch2

-24–12 (semi)
Adjusts the amount that PITCH1 or PITCH2 is pitch-shifted.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and
effect sound.

## Pan1, Pan2


## L50–R50

Sets the panning of PITCH1 or PITCH2.
Hyper-Reso
This is a resonator effect that is adjusted to make creating melodies and bass lines easier.
Parameter
Value
Explanation

## Note

-17– -1, 1–18
Sets which note in the chromatic scale should resonate,
counting from the root of the SCALE value.

## Spread


## Unison, Tiny, Small, Medium, Huge

Sets the octave of the resonator.

## Character

0–100
Adjusts the brightness and detuning of the sound.

## Scale

C Maj–B Maj, C min–B min
Sets the composite notes (chord) to resonate.

## Feedback

0–99 (%)
Adjusts the amount of feedback for the effect.

## Env Mod

0–100
Larger values increase the amount of feedback
according to the input level.
Ring Mod
This effect alters the tonal character to make the sound more metallic.
Parameter
Value
Explanation

## Frequency

0–100
Sets the frequency range to which the effect is applied.

## Sens

0–100
Adjusts the volume of the effect sound.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect sound.

## Polarity


## Off, On

Sets the direction in which the frequency modulation moves.

## Eq Low

-15–15 (dB)
Adjusts the amount of boost/cut of the low-frequency range.

## Eq High

-15–15 (dB)
Adjusts the amount of boost/cut of the high-frequency range.
Crusher
Produces a lo-fi effect.
Appendix
Parameter
Value
Explanation

## Filter

331–15392 (Hz)
Sets the frequency range in which the pre-filter (the filter that the sound passes
through before effects are applied) works.

## Rate

0–100
Sets the sample rate of the effect. Larger values make the sample rate lower, for a
more lo-fi sound.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect sound.
Overdrive
Mildly distorts the sound.
Parameter
Value
Explanation

## Drive

0–100
Adjusts the amount of distortion.

## Tone

-100–100
Sets the tone. Larger settings emphasize the high-frequency range. Smaller settings
emphasize the low-frequency range.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect sound.

## Level

0–100
Adjusts the volume of the effect sound.
Distortion
Intensely distorts the sound.
Parameter
Value
Explanation

## Drive

0–100
Adjusts the amount of distortion.

## Tone

-100–100
Sets the tone. Larger settings emphasize the high-frequency range. Smaller settings
emphasize the low-frequency range.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect sound.

## Level

0–100
Adjusts the volume of the effect sound.
Equalizer
This is a three-band equalizer.
Parameter
Value
Explanation

## Low Gain

-15–15 (dB)
Adjusts the amount of
boost/cut of the low-
frequency range.

## Mid Gain

-15–15 (dB)
Adjusts the amount of
boost/cut of the mid-
frequency range.

## High Gain

-15–15 (dB)
Adjusts the amount of
boost/cut of the high-
frequency range.

## Low Freq

20, 25, 31, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400 (Hz)
Sets the low-frequency
range.
Mid Freq
200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300,
8000 (Hz)
Sets the mid-frequency
range.

## High Freq

2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000 (Hz)
Sets the high-frequency
range.
Compressor
This effect reduces high volume levels while bringing up the level of quieter sounds, smoothing out any variations in overall volume.
Appendix
Parameter
Value
Explanation

## Sustain

0–100
Sets how long the effect is applied to the decaying sound.

## Attack

0–100
Sets how long it takes to reduce the volume when a high input level is detected.

## Ratio

0–100
Sets the compression ratio.

## Level

0–100
Adjusts the volume of the effect sound.

## Note

This effect may output a very loud sound, depending on how the parameters are set. Use caution not to raise the values too much.
SX Reverb
This adds reverberation to the sound.
As with the SP-404SX, you can adjust the volume balance between the dry (original) sound and the effect sound with this effect.
Parameter
Value
Explanation

## Time

0–100
Sets the reverb time.

## Tone

-100–100
Adjusts the tonal character of the reverb.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect sound.
SX Delay
Gives an echo effect in sync with the tempo.
As with the SP-404SX, you can adjust the volume balance between the dry (original) sound and the effect sound with this effect.
Parameter
Value
Explanation

## Time

1/32, 1/16T, 1/32D, 1/16, 1/8T, 1/16D, 1/8, 1/4T, 1/8D, 1/4, 1/2T, 1/4D,

## 1/2, 1/1T, 1/2D, 1/1

Sets the sound delay time.

## Feedback

0–99 (%)
Adjusts the amount of feedback for the
effect.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the
dry (original) sound and effect sound.
Cloud Delay
Adds multiple delays to the dry sound, as well as reverberations for a thick “cloudy” effect.
Parameter
Value
Explanation

## Window

0–100
Adjusts the interval for the delayed sound.
Larger settings produce a deeper reverberation.

## Pitch

-12.0–+12.0
Adjusts the volume of the pitch shifter for the effect sound.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and effect
sound.

## Feedback

-100–100
Adjusts the amount of feedback for the effect.

## Cloudy

0–100
Adjusts the thickness of the effect sound.

## Lofi


## Off, On

When this is ON, the tonal character of the effect sound is degraded.
Back Spin
This gives the effect of spinning a record backwards.
Parameter
Value
Explanation

## Length

1/1, 1/2, 1/4, 1/8, 1/16
Sets the length of the back spin.

## Speed

0–100
Sets the speed of the back spin.
Appendix
Parameter
Value
Explanation

## Back Sw


## Off, On

If you turn this ON while a sound is playing, the back spin plays for a length of time
specified by the LENGTH parameter.
Turn this OFF to disable the back spin.

## Memo

After switching to this effect, the sample must be played back (charged) for up to
approximately three seconds.
The BACK SW parameter blinks during charging.
DJFX Delay
This is a combination effect that uses both DJFX Looper (p. 129) and TimeCtrlDly (p. 132).
Parameter
Value
Explanation

## Length

0.230–0.012 (sec)
Sets the length of the loop.

## Time

0–100 (msec) (when the SYNC parameter
is OFF)

## 1/32, 1/16T, 1/32D, 1/16, 1/8T, 1/16D, 1/8,


## 1/4T, 1/8D, 1/4, 1/2T, 1/4D, 1/2, 1/1T, 1/2D,

1/1 (when the SYNC parameter is ON)
Sets the sound delay time.

## Loop Sw


## Off, On

Turn this ON while a sound is playing to make the sound play back in a
loop, at a length specified by the LENGTH parameter.
* Delay is applied only when LOOP SW is ON. Turn this OFF to disable
the loop.

## Feedback

0–99
Adjusts the amount of feedback for the delay.

## Level

0–100
Sets the volume of the delay.

## Sync


## Off, On

When this is ON, the effect sound synchronizes with the tempo.
Auto Pitch
Processes the human voice to create a variety of characters.
* This is enabled with INPUT FX.
Parameter
Value
Explanation

## Pitch

-100–100
Sets the pitch of the voice. You can change the pitch up and down one
octave.

## Formant

-100–100
Sets the formant of the voice. Lower settings give a more masculine
vocal character, and higher settings give a more feminine vocal
character.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original) sound and
effect sound.

## At Pitch

0–100
Adjusts the strength at which the pitch is corrected.

## Key


## Chroma, A, B' , B, C, D' , D, E' , E, F, G' , G,


## A'

Adjusts the key to which the pitch is corrected.

## Robot


## Off, On

When this is turned ON, the inputted voice is altered to a voice without
inflection, staying at the same pitch.
Vocoder
Changes the voice to a vocoder voice.
Appendix
* This is enabled with INPUT FX.
Parameter
Value
Explanation

## Note

-17– -1, 1–18
Sets which note in the chromatic scale should sound, counting from
the root of the SCALE value. The scale and chord structure that is used
depends on the SCALE and CHORD settings.

## Memo

The NOTE value can be controlled via note messages from a MIDI
keyboard connected to the MIDI IN connector, a computer connected
via USB, a DAW app running on an iOS device and so on.
At that time, you can send pitch bend messages to continuously
change the pitch.
For note messages (Note Number = 0–127) and pitch bend messages,
set the MIDI channel on your external device to “11”.

## Formant

-100–100
Adjusts the formant of the voice. Lower settings give a more masculine
vocal character, and higher settings give a more feminine vocal
character.

## Tone

-100–100
Adjusts the brightness of the effect sound.

## Scale

C Maj–B Maj, C min–B min
Sets the scale to use and its root.

## Chord

Root, P5, Oct, UpDn, UpDnP5, 3rd, 5thUp,
5thDn, 7thUp, 7thDn
Sets the chord structure.

## Balance

100-0–0-100
Adjusts the volume balance between the dry (original) sound and
effect sound.
Harmony
This effect adds a harmony to your voice.
Parameter
Value
Explanation

## Pitch

-100–100
Sets the pitch of the voice. You can change the pitch up
and down one octave.

## Formant

-100–100
Sets the formant of the voice.
Lower settings give a more masculine vocal character,
and higher settings give a more feminine vocal
character.

## Balance

100-0–0-100 (%)
Adjusts the volume balance between the dry (original)
sound and effect sound.

## At Pitch

0–100
Adjusts the strength at which the pitch is corrected.

## Key

CHROMA, A, B' , B, C, D' , D, E' , E, F, G' , G, A'
Sets the key to which the pitch is adjusted and the
harmonies are added.

## Harmony

Root, P5, Oct, UpDn, UpDnP5, 3rd, 5thUp, 5thDn, 7thUp,
7thDn
Sets the harmonization.
Gt Amp Sim
This effect models a guitar amplifier.
* This is enabled with INPUT FX.
Appendix
Parameter
Value
Explanation

## Amp Type

Selects the guitar amp type.

## Jc

Models the sound of a Roland JC-120.

## Twin

Models a Fender Twin Reverb.

## Bg

Models a lead guitar sound played using a MESA/Boogie combo amp.

## Match

Models a Matchless D/C-30.

## Ms

Models a Marshall 1959.

## Sldn

Models a Soldano SLO-100.

## Drive

0–100
Adjusts the volume and distortion of the amp.

## Level

0–100
Adjusts the volume of the effect sound.

## Bass

-100–100
Adjusts the low-frequency tonal character.

## Middle

-100–100
Adjusts the midrange tonal character.

## Treble

-100–100
Adjusts the high-frequency tonal character.
Control change messages and corresponding effects
You can use a control change message (CC#83) to select the effects.
The effects (selectable effects) corresponding to the respective CC#83 values are shown below.
BUS1 (MIDI ch 1), BUS2 (MIDI ch 2)
Value of CC#83
Effect name

## (Off)

Direct FX1
Direct FX2
Direct FX3
Direct FX4
Direct FX5
Scatter
Downer
Ha-Dou
Ko-Da-Ma
Zan-Zou
To-Gu-Ro

## Sbf

Stopper
Tape Echo
TimeCtrlDly
Super Filter
WrmSaturator
303 VinylSim
404 VinylSim
Cassette Sim
Lo-fi
Reverb
Appendix
Value of CC#83
Effect name
Chorus
JUNO Chorus
Flanger
Phaser
Wah
Slicer
Tremolo/Pan
Chromatic PS
Hyper-Reso
Ring Mod
Crusher
Overdrive
Distortion
Equalizer
Compressor
SX Reverb
SX Delay
Cloud Delay
Back Spin
DJFX Delay
43–127
BUS3 (MIDI ch 3), BUS4 (MIDI ch 4)
Value of CC#83
Effect name

## (Off)

303 VinylSim
404 VinylSim
Cassette Sim
Lo-fi
Downer
Compressor
Equalizer
Isolator
Super Filter
Filter+Drive
WrmSaturator
Overdrive
Distortion
Crusher
Ring Mod

## Sbf

Appendix
Value of CC#83
Effect name
Resonator
Hyper-Reso
Chromatic PS
Reverb
Ha-Dou
Zan-Zou
Sync Delay
TimeCtrlDly
Ko-Da-Ma
Tape Echo
Chorus
JUNO Chorus
Flanger
Phaser
Wah
Slicer
Tremolo/Pan
To-Gu-Ro
DJFX Looper
Scatter
SX Reverb
SX Delay
Cloud Delay
DJFX Delay
41–127
INPUT FX (MIDI ch 5)
Value of CC#83
Effect name

## (Off)

Auto Pitch
Vocoder
Harmony
Gt Amp Sim
Chorus
JUNO Chorus
Reverb
TimeCtrlDly
Chromatic PS
Downer
WrmSaturator
303 VinylSim
Appendix
Value of CC#83
Effect name
404 VinylSim
Cassette Sim
Lo-fi
Equalizer
Compressor
18–127
List of shortcut keys
You can quickly recall a desired function or screen by pressing a button or pad while holding down the [SHIFT] button.
Shortcuts that use the [SHIFT] button
While holding down the [SHIFT] button
Function
Explanation
Pad [1]

## Fixed Velocity

Sets the sample’s velocity so that it always plays back at 127 (the maximum).
Pad [2]

## 16 Velocity

Changes a sample’s velocity (volume) in steps when it plays back.
Pad [3]

## Cue

Adjusts the balance of the audio you monitor via the PHONES jack.
Pad [4]

## Chromatic

Lets you play back samples (changing their pitches) as a chromatic scale with
the pads.
Pad [5]

## Exchange

Exchanges (swaps) the sample or pattern data saved in different pads.
Pad [6]

## Init Param

Initializes the sample parameters for the selected pad.
Pad [7]

## Pad Link

Lets you play back all the pads at the same time that are assigned to a group,
by using a single pad.
Pad [8]

## Mute Group

Groups together samples that you don’t want to play together (samples that
you don’t want layered).
Pad [9]

## Metronome

Turns the metronome on/off.
Pad [10]

## Count-In

Adds a count-in before sampling or pattern recording begins.
Pad [11]

## Tap Tempo

Lets you set the tempo in an intuitive way by tapping the pad in time, as if you
were clapping out the beat.
Pad [12]

## Gain

Displays the UTILITY MENU > SYSTEM > GAIN tab.
Pad [13]

## Utility

Displays the UTILITY MENU screen.
Pad [14]

## Import/Export

Displays the UTILITY MENU > IMPORT (IMPORT/EXPORT MENU).
Pad [15]

## Pad Setting

Displays the UTILITY MENU > PAD SET (PAD SETTING).
Pad [16]

## Efx Setting

Displays the UTILITY MENU > EFX SET (EFX SETTING) screen.
[BUS FX] button

## Mute Bus

Temporarily turns off the audio sent to the bus (the sample playback sound or
the sound inputted to the INPUT jack), and outputs only the sound of the
effect.
[HOLD] button

## Pause

Pauses the sample that’s currently playing back.
[EXT SOURCE] button

## Input Setting

Displays the input settings screen.
[SUB PAD] button

## Project

Displays the SELECT PROJECT screen.
[MARK] button (at least three seconds)

## Save Efx


## Parameter

Saves the main parameters of the effects assigned to BUS 1 and BUS 2.
[PITCH/SPEED] button

## Envelope

Sets how the volume changes when the sample plays back.
[START/END] button

## Chop

Splits the sample at the marker positions, and assigns the resulting samples to
separate pads.
Appendix
While holding down the [SHIFT] button
Function
Explanation
[PATTERN SELECT] button

## Undo

Undoes the data you just inputted (recorded).
* Enabled only when recording a pattern
[ROLL] button

## Roll Set

This shows how to set the roll interval (how fast the roll repeats).
[REVERSE] button + pads [1]–[16]
Pad MUTE
Switches the pad mute on/off.
[REVERSE] button + [REMAIN] button
Pad MUTE MODE
Keeps the [SHIFT] and [REVERSE] buttons in “pressed-down” state.
[LOOP] button

## Ping-Pong Loop

Loops the sample by repeatedly playing back forward and then backward.
[GATE] button

## Gate All On/Off

Turns the GATE parameter for all samples in the selected bank on/off.
[BPM SYNC] button

## Sync All On/Off

Turns the BPM SYNC parameter for all samples in the selected bank on/off.
[REC] button

## Tr-Rec

Switches to pattern recording using TR-REC.
This lets you record a sample onto the pattern that’s playing back.
* Enabled only when playing back a pattern
Bank [A/F]–[E/J] buttons

## Bank Volume

Adjusts the volume for the specified bank overall.
[REMAIN] button (at least three seconds)

## Live Mode

Use this to disable buttons that are not used when playing live (sampling and
edit-related buttons).
[COPY] button

## Bank Protect

This function prevents the samples and patterns assigned to a pad from being
copied, overwritten by editing or accidentally deleted.
[VALUE] knob (press)

## Mark

Switches the function to be recalled when you press the [MARK] button.
* Switches between “SBS *** (skip-back sampling)” and “Looper”.
[RESAMPLE] button

## Sample Merge


## Mode

Switches to sample merge mode.
[RECORD SETTING] button

## Sound


## Generator Mode

Switches to sound generator mode.
[EXIT] button

## Stop

Stops the playback of all samples.
Shortcuts that use the [REMAIN] button
While holding down the [REMAIN] button
Function (explanation)
Pads [1]–[16]
Sets which sample playback audio is sent to which bus (meaning which effects are
used) for each sample.
Bank [A/F]–[E/J] buttons
Sets the bus send destination for all samples in a bank.
[MFX] button
Makes the effect edit screen keep displaying.
[BUS FX] button
You can swap the effects of BUS 1 and BUS 2. When the effects are switched, the effect
parameter values are retained.
Edits the following parameters on the pitch/speed
settings screen

## Speed


## Pitch


## Volume


## Pan


## Bpm


## Bpm Sync


## Gate


## Loop


## Reverse

Lets you simultaneously edit the parameters of samples that are registered to the
same bank.
Appendix
While holding down the [REMAIN] button
Function (explanation)
Edits the following parameters on the envelope settings
screen

## Attack


## Hold


## Release


## Bpm Sync


## Gate


## Loop


## Reverse

Lets you simultaneously edit the parameters of samples that are registered to the
same bank.
Shortcuts that use the [VALUE] button
While holding down the [VALUE] knob
Function (explanation)
Pads [1]–[16]
Selects a sample (no sound is produced).
Also, selects a pattern when [PATTERN SELECT] is lit (the pattern does not play back).
[BUS FX] button
Temporarily bypasses BUS 3 and BUS 4.
[SUB PAD] button
This minimizes the slight differences in timing when you play multiple samples at the
same time.
Effect buttons ([FILTER+DRIVE]–[MFX] button)
Applies effects only while you hold down the effect buttons (EFFECT GRAB).
[GATE] button
Switches the “one-shot playback” sample playback mode on/off.
Shortcuts that use the [DEL] button
While holding down the [DEL] button
Function (explanation)
[MARK] button
Deletes the effect operations recorded using EFX MOTION REC from a pattern.
* Enabled on the pattern edit screen
[REVERSE] button
Deletes the pad mute operations recorded using EFX MOTION REC from a
pattern.
* Enabled on the pattern edit screen
[EXIT] button
Deletes all samples or patterns in a bank.
Shortcuts that use the [COPY] button
While holding down the [COPY] button
Function (explanation)
Edits the following parameters on the pitch/speed
settings screen

## Speed


## Pitch


## Volume


## Pan


## Bpm


## Bpm Sync


## Gate


## Loop


## Reverse

Lets you simultaneously edit the parameters of samples that are registered to the
same mute group.
Appendix
While holding down the [COPY] button
Function (explanation)
Edits the following parameters on the envelope settings
screen

## Attack


## Hold


## Release


## Bpm Sync


## Gate


## Loop


## Reverse

Lets you simultaneously edit the parameters of samples that are registered to the
same mute group.
[EXIT] button
Copies all samples or patterns in a bank to a different bank.
Shortcuts that use the [MFX] button
While holding down the [MFX] button
Function (explanation)
[DJFX LOOPER] button
Displays the MFX LIST from #17 onwards.
[ISOLATOR] button
Displays the MFX LIST from #33 onwards.
Shortcuts used in DJ mode
Operation
Parameter
Explanation
[SHIFT] button + [REVERSE] button + pad

## [13] (Ch1)

[SHIFT] button + [REVERSE] button + pad

## [15] (Ch2)


## Mute

Mutes the sample that’s playing back.
[SHIFT] button + pads [1]–[16]
You can play back a sample from the position of the marker that’s set
for that sample.
[SHIFT] button + [REMAIN] button
The [SHIFT] button remains in a “pressed-down” state. This makes it
easier to select a marker and play back.
Press the [EXIT] button to cancel this behavior.
[SHIFT] button + [MARK] button
You can add markers while playing samples in DJ mode.
[SHIFT] button + [START/END] button
You can edit markers while playing samples in DJ mode.
[SHIFT] button + [DEL] button + pads [1]–
[16]
While in DJ mode, you can delete the markers you’ve set for samples.
[SHIFT] button + [ROLL] button

## Roll Size

Sets the roll interval (1/4, 1/2, 1 or 2 measures).
Set the ROLL SIZE before playing back rolls. (You can’t change the ROLL
SIZE with this operation while a roll is playing back).
[ROLL] button + pad [13] (CH1)
[ROLL] button + pad [15] (CH2)
Repeats the sample playback in more detailed intervals (ROLL).
Note that when the ROLL SIZE (roll interval) is longer than the sample
length, a roll cannot played back.
[ROLL] button + pads [1]–[4]
Changes the roll interval while the roll is playing back.
[ROLL] button + pad [1]: quarter-note (1/4 of a measure)
[ROLL] button + pad [2]: half-note (1/2 of a measure)
[ROLL] button + pad [3]: whole note (1 measure)
[ROLL] button + pad [4]: two whole notes (2 measures)
[REMAIN] + pad [14] (CH1)
[REMAIN] + pad [16] (CH2)

## Bus Fx

You can set the bus to which the CH1/CH2 sample playback is sent
(meaning which effects are used).
While holding down the [REMAIN] button, each time you press pad [14]
or pad [16] switches the effect to use as follows: “BUS-1”

## “Bus-2”


## “Dry”


## “Bus-1”.

Appendix
Operation
Parameter
Explanation
Press [RESAMPLE] button + [VALUE] knob

## Volume Curve

Selects the volume curve characteristics used for each slider (CH1
LEVEL, CH2 LEVEL, X-FADE) in DJ mode.
Each time you hold down the [RESAMPLE] button and press the
[VALUE] knob, the characteristic switches in this order: “FAST CUT”

## “Linear”


## “Square”


## “Cubic”


## “Fast Cut”.

[DEL] button + pad [2] + pad [6] (CH1)
[DEL] button + pad [4] + pad [8] (CH2)

## Bpm

Resets the tempo to the default value.
[START/END] button
Switches between the functions (CUE MIX or X-FADE) for the [CTRL 3]
knob.
[PITCH/SPEED] button
Changes the number of digits shown for the BPM.
Each time you press the [PITCH/SPEED] button, the display switches in
the following order: integers only
to the second decimal place
to
the first decimal place
integers only....
When you set the BPM value using pads [2] [4] (BPM+) and pads [6] [8]
(BPM-), the number of digits shown for the BPM changes according to
the minimum unit.
[MARK] button
Switches between the EFX and MIXER screen views.
[BPM SYNC] button
Selects the channel (CH1/CH2) used to control reverse playback
([REVERSE] button).
Shortcuts used in TR-REC
Operation
Explanation
[DEL] button + [A/F] button
Deletes the notes (for one measure) corresponding to the selected
pad.
[DEL] button + [B/G] button
Deletes the notes (for one measure) corresponding to all pads.
[ROLL] button + [CTRL 1] knob
You can record the motion of [CTRL 1] knob in the steps.
* This is enabled when MODE is “TRIG”.
[ROLL] button + [CTRL 2] knob
You can record the motion of [CTRL 2] knob in the steps.
* This is enabled when MODE is “TRIG”.
[ROLL] button + [CTRL 3] knob
You can record the motion of [CTRL 3] knob in the steps.
* This is enabled when MODE is “TRIG”.
[VALUE] knob (press) + [SUB PAD] button + pads [1]–[16]
You can select samples without playing them back.
Error messages
Error messages
Explanation
Action
Battery Low!
The batteries are nearly depleted.
Replace the batteries, or switch to an AC adaptor.
“About the power supply (p. 14)”
Unsupported FILE
The file type is not supported on
this unit.
Check the file extension, format and folder directory.
“Importing/exporting (using the SD card) (p. 110)”
No SD CARD!
No SD card is inserted. Also, the SD
card might not be fully inserted.
Turn off the power, and make sure that the SD card is fully inserted before you
turn the power back on.
Unsupported SD Card!
An unsupported type of SD card
has been inserted.
Please format the SD card.
“Formatting an SD card (p. 119)”
SD CARD Protected!
The write-protect feature has been
enabled on the SD card.
Unlock the lock switch on the left side of the SD card.
SD CARD Full!
The SD card has run out of free
space.
Delete any unneeded data on the unit.
Appendix
Error messages
Explanation
Action
Internal Storage Full!
There is not enough storage
capacity left on this unit.
Delete any unneeded data on the unit.
Storage Error!
A problem has occurred with the
internal storage.
Try performing a factory reset.
“Restoring the factory settings (FACTORY RESET) (p. 119)”
Protected!
The function can’t be executed
because bank protect is enabled.
Use a bank for which bank protect is disabled, or disable bank protect on the
currently selected bank.
“Selecting a sample bank (p. 17)” “Selecting a pattern bank (p. 67)”
“Protecting a sample (PROTECT) (p. 56)” “Protecting a pattern (PROTECT) (p.
79)”
Max Length Pattern
The maximum number of notes
that can be recorded to the
pattern sequencer has been
exceeded.
Reduce the number of notes in the pattern, or shorten and split the pattern to
record.
“Creating a new pattern (real-time recording) (p. 58)”
Audio diagram
Main specifications
Maximum polyphony
32 voices
Recordable data
Samples: 2,560 (16 samples x 10 banks x 16 projects: stored in internal storage)
Patterns: 2,560 (16 patterns x 10 banks x 16 projects: stored in internal storage)
Internal storage
Size: 16 GB
* Include preload data
Maximum sampling time
16 minutes (approximately 185 MB per sample)
Skip back sampling time
Maximum 40 seconds (Always records LINE OUT signal independently of sampling/resample)
Internal data format
16-bit linear
Import format

## Wav, Aiff, Mp3

* SP-404MK2 App supports WAV, AIFF, MP3, FLAC, M4A.
Sample rate
48 kHz
Pattern sequencer
Resolution : 480 ticks per quarter note
Pattern length: 1 to 64 bars
Recording methods: Realtime loop recording, TR-REC (Automation supported)
Effects
Multi-effects: 42 types
Input effects: 17 types
Pads
16 pads + 1 sub pad (Velocity-sensitive pad)
Appendix
Controllers
Control knob x 3
Display
Graphic OLED display
External storage
SD card (SDHC compatible, commercially available)
* For backup, restore, import, and export functions
Connection terminals
PHONES jacks: 1/4-inch phone type, Stereo miniature phone type
LINE OUT (L/MONO, R) jacks: 1/4-inch TRS phone type (impedance balanced)
LINE IN (L/MONO, R) jacks: 1/4-inch phone type
MIC/GUITAR IN jacks: 1/4-inch TRS phone type (for MIC), 1/4-inch phone type (for GUITAR)
MIDI (IN, OUT) jack: Stereo miniature phone type
USB port: USB Type-C® (Audio, MIDI)
DC IN jack
Power supply
AC adaptor
USB bus power supply (USB Type-C® port, 1.5 A or more)
Ni-MH battery (AA, HR6, commercially available) x 6 or Alkaline battery (AA, LR6, commercially
available) x 6
Current draw
1,100 mA (AC adaptor)
1,500 mA (USB bus power)
Expected battery life under continuous
use
Alkaline battery: Approx. 2.5 hours
Ni-MH battery: Approx. 3.5 hours
* This can vary depending on the specifications of the batteries, capacity of the batteries, and the
conditions of use.
External dimensions
178 (W) x 276 (D) x 71 (H) mm
7 (W) x 10-7/8 (D) x 2-13/16 (H) inches
Weight (excluding AC adaptor)
1.1kg
2 lbs 7 oz
Accessories
Quick Start
“Read Me First” leaflet
AC adaptor
Options (sold separately)
TRS/MIDI connecting cable: BOSS BMIDI series, BOSS BCC series
Wireless MIDI Expression Pedal: BOSS EV-1-WL
Wireless Footswitch: BOSS FS-1-WL
* This document explains the specifications of the product at the time that the document was issued. For the latest information, refer to the
Roland website.
MIDI implementation chart
Model: SP-404MK2
Date: Jul. 01, 2025
Version: 5
Function
Transmitted
Recognized
Notes
Basic Channel
Default
x (MIDI mode A)
1–10 (MIDI mode B)
x (MIDI mode A)
1–10 (MIDI mode B)
*1
Changed
x (MIDI mode A)
1–10 (MIDI mode B)
x (MIDI mode A)
1–10 (MIDI mode B)
*1
Mode
Default
Mode 3
Messages
Altered
Appendix
Function
Transmitted
Recognized
Notes
Note Number
35–51 (B1–E' 3, MIDI mode

## A) *1


## 0, 12–91 (C-1, C0–G6, Midi

mode B) *1

## 36–60 (C2–C4, Ch 16) *7

35–51 (B1–E' 3, MIDI mode

## A) *1


## 0, 12–91 (C-1, C0–G6, Midi

mode B) *1

## 0–127 (Ch 11) *2


## 36–60 (C2–C4, Ch 16) *6

True Voice
36–51 (C2–E' 3, MIDI mode

## A) *1

12–91 (C0–G6, MIDI mode B)
*1
Velocity
Note On
Note Off
Aftertouch
Key’s
Channel’s
Pitch Bend
o *2
Control
Change

## Cc#16–19

o *7
Example:
0xB0 10 00
BUS 1 Ctrl 1=0
0xB1 13 7F
BUS 2 EFX switch = ON

## Cc#80–83

o *7
Example:
0xB2 50 7F
BUS 3 Ctrl 4=127
0xB3 53 01
BUS 4 EFX number = 01
(303 VinylSim)

## Cc#07

o *8
o *8
Example:
0xB1 07 7F
CH2 volume slider = 127

## Cc#08

o *8
o *8
Example:
0xB0 08 7F

## X-Fade = 0:127 (Ch1 = 0,


## Ch2 = 127)


## Cc#20–27

o *8
Example:
0xB0 14 01
CH1 play
0xB2 1A 7F
press the pattern
sequencer [BPM+] button
Program Change
o *1 *9
Example:
0xC3 0F
Bank D Pattern 16
System Exclusive
System
Common
Song Position
Song Select
Tune Request
System
Realtime
Clock
o *3
o *4
Commands
o *3
o *4
Aux Messages
All Sound Off
o *5
Reset All Controllers
Local On/Off
All Notes Off
Active Sensing
System Reset
Appendix
Notes
*1
Refer to “MIDI note map (p. 154)”.
*2
Enabled when INPUT FX is “Vocoder” (MIDI CH 11).
*3
Output when MIDI Sync Out is “ON” and when there is no tempo input from an external device.
*4
Enabled when this unit is in remote mode (when a tempo signal is received from an external device).
*5
All samples stop playing back when the MIDI cable is unplugged.
*6
Enabled when playing samples in chromatic mode (MIDI CH 16).
*7 MIDI channels

## Ch 1: Bus 1


## Ch 2: Bus 2


## Ch 3: Bus 3


## Ch 4: Bus 4


## Ch 5: Input

*7 Control change message numbers and corresponding EFX controls

## Cc#19

EFX switch (0–63: OFF, 64–127: ON)

## Cc#83

EFX number (0–127)
“Control change messages and corresponding effects (p. 142)”

## Cc#16

Ctrl 1 (0–127)

## Cc#17

Ctrl 2 (0–127)

## Cc#18

Ctrl 3 (0–127)

## Cc#80

Ctrl 4 (0–127)

## Cc#81

Ctrl 5 (0–127)

## Cc#82

Ctrl 6 (0–127)
*8 Control change message numbers and corresponding controllers in DJ mode
MIDI channel 1 (CH1 sample)
MIDI channel 2 (CH2 sample)
MIDI channels 3 (pattern sequencer)

## Cc#7

[Ctrl 1] knob: CH1 volume slider (0–127)
[Ctrl 2] knob: CH2 volume slider (0–127)
[Ctrl 1] knob: pattern sequencer volume
slider (0–127)

## Cc#8

[Ctrl 3] knob: X-FADE (CH1: CH2 = 127:0–
0:127)

## Cc#20

[%
] button (0: pause, 127: play)
[%
] button (0: pause, 127: play)
[%
] button (0: pause, 127: play)

## Cc#21

[&
] button (0: release the button, 127: press
the button)
[&
] button (0: release the button, 127:
press the button)
[&
] button (0: release the button, 127: press
the button)

## Cc#22

[SYNC] button (0: Off, 127: On)
[SYNC] button (0: Off, 127: On)
[SYNC] button (0: Off, 127: On)

## Cc#23

[CUE] button (0: Off, 127: On)
[CUE] button (0: Off, 127: On)
[CUE] button (0: Off, 127: On)

## Cc#24

[BEND+] button (0: release the button, 127:
press the button)
[BEND+] button (0: release the button,
127: press the button)
[BEND+] button (0: release the button, 127:
press the button)

## Cc#25

[BEND-] button (0: release the button, 127:
press the button)
[BEND-] button (0: release the button,
127: press the button)
[BEND-] button (0: release the button, 127:
press the button)

## Cc#26

[BPM+] button (0: release the button, 127:
press the button)
[BPM+] button (0: release the button,
127: press the button)
[BPM+] button (0: release the button, 127:
press the button)

## Cc#27

[BPM-] button (0: release the button, 127:
press the button)
[BPM-] button (0: release the button,
127: press the button)
[BPM-] button (0: release the button, 127:
press the button)
Appendix
*8 Control change message numbers and corresponding controllers in Looper mode
MIDI channel: 1

## Cc#87

[DEL] button
Deletes the sampled content.

## Cc#88

[REC] button
Stops sampling.
Starts sampling.

## Cc#89

[RESAMPLE] button
Activates overdubbing mode.

## Cc#90

[CTRL 3] knob
0–127
Adjusts the value of BPM/PLAY-RATE parameters.

## Cc#85

[EXIT] button
Stops the playback of all samples by quickly pressing the
button four times.

## Cc#86

[PITCH/SPEED] button
Resets the tempo setting.

## Cc#91

[SHIFT] button + [PATTERN
SELECT] button
Cancels the undo action (REDO).
Undoes (UNDO) the data you just input (recorded).
Program change numbers and corresponding patterns

## Pc#0

Pattern 1

## Pc#1

Pattern 2

## Pc#15

Pattern 16
Mode 1: OMNI ON, POLY
Mode 2: OMNI ON, MONO
Mode 3: OMNI OFF, POLY
Mode 4: OMNI OFF, MONO
o: Yes
x: No
MIDI note map
MIDI Mode
MIDI Channel

## Ch 1

...

## Ch 10


## Ch 1–9


## Ch 2–10

Note Number

## Bank


## Pad

...

## Bank


## Pad


## Bank


## Pad


## Bank


## Pad


## G9

Blank
...
Blank
Blank (for Note Offset)
Blank (for Note Offset)
Blank
...
Blank
Blank (for Note Offset)
Blank (for Note Offset)

## A' 6

Blank
...
Blank
Blank (for Note Offset)
Blank (for Note Offset)

## G6

Blank
...
Blank

## F(6

Blank
...
Blank

## F6

Blank
...
Blank

## E6

Blank
...
Blank

## E' 6

Blank
...
Blank

## D6

Blank
...
Blank