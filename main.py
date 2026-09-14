import sys
import time
import librosa
import librosa.display
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pretty_midi
import pygame
import argparse

parser = argparse.ArgumentParser(description = "convert audio transients to midi")
parser.add_argument('filename', nargs = "?", default = "drums.mp3")
args = parser.parse_args()

# ==========================================
# 1. LOAD AUDIO & DETECT TRANSIENTS
# ==========================================


audio_path = args.filename


y, sr = librosa.load(audio_path)
hop_length = 512
duration = librosa.get_duration(y=y, sr=sr)

# Process audio features
stft = librosa.stft(y, hop_length=hop_length)
amplitude_envelope = np.max(np.abs(stft), axis=0)
envelope_time = librosa.frames_to_time(
    np.arange(len(amplitude_envelope)), sr=sr, hop_length=hop_length
)

# Onset detection
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
onset_time = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)

# ==========================================
# 2. GENERATE & SAVE MIDI
# ==========================================

pm = pretty_midi.PrettyMIDI()
drum_kit = pretty_midi.Instrument(program=0, is_drum=True)
for start_time in onset_time:
    note = pretty_midi.Note(
        velocity=100, pitch=36, start=start_time, end=start_time + 0.1
    )
    drum_kit.notes.append(note)
pm.instruments.append(drum_kit)
pm.write("detected_transients.mid")

# ==========================================
# 3. SET UP GUI PLOT LAYOUT (THE DAW)
# ==========================================

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(12, 6), sharex=True, gridspec_kw={"height_ratios":[1,1]}
)
fig.canvas.manager.set_window_title("Python DAW Previewer (Press 'Z' to Zoom)")

# Track 1: Audio Waveform
librosa.display.waveshow(y, sr=sr, alpha=0.6, color="blue", ax=ax1)
ax1.set_title("Audio Track (Waveform)")
ax1.set_ylabel("Amplitude")

# Track 2: MIDI Piano Roll / Drum Grid
for onset in onset_time:
    ax2.plot(
        [onset, onset + 0.1],
        color="lime",
        solid_capstyle="butt",
        linewidth=8,
    )

# Visualise transient vertical alignment lines

ax2.vlines(
    onset_time, 35, 37, color="g", linestyle="dashed", alpha=0.4, label="Onsets"
)
ax2.set_title("MIDI Track (Kick Drum - Note 36)")
ax2.set_ylabel("MIDI Note")
ax2.set_ylim(35, 37)
ax2.set_yticks([36])
ax2.set_yticklabels(["Kick (36)"])
ax2.set_xlabel("Time (seconds)")
ax2.set_xlim(0, duration)

# Draw the initial Playhead Lines on both tracks
playhead1 = ax1.axvline(x=0, color="red", linestyle="-", linewidth=2)
playhead2 = ax2.axvline(x=0, color="red", linestyle="-", linewidth=2)

plt.tight_layout()

# ==========================================
# 4. ZOOM & KEYBOARD CONTROLS
# ==========================================

# Zoom configuration states
is_zoomed = False
zoom_window = 5.0  # Seconds shown on screen when zoomed in


def on_key_press(event):
    """Listens for the 'z' key to toggle the zoom view state."""
    global is_zoomed
    if event.key == "z" or event.key == "Z":
        is_zoomed = not is_zoomed
        if not is_zoomed:
            # Instantly snap back to the full overview
            ax2.set_xlim(0, duration)
            fig.canvas.draw_idle()


# Connect the keyboard listener to the active window figure
fig.canvas.mpl_connect("key_press_event", on_key_press)

# ==========================================
# 5. LIVE PLAYBACK & ANIMATION ENGINE
# ==========================================

pygame.mixer.init()
pygame.mixer.music.load(audio_path)

audio_start_time = None


def init_playback():
    """Starts the audio device at the absolute beginning."""
    global audio_start_time
    pygame.mixer.music.play()
    audio_start_time = time.time()
    return playhead1, playhead2


def update_playhead(frame):
    """Updates playhead position and dynamically adjusts axes limits if zoomed."""
    if pygame.mixer.music.get_busy():
        current_time = pygame.mixer.music.get_pos() / 1000.0

        # Push the vertical visual lines forward
        playhead1.set_xdata([current_time])
        playhead2.set_xdata([current_time])

        # Dynamic Scrolling Zoom Logic
        if is_zoomed:
            # Center the window around the playhead, clamped to track edges
            half_window = zoom_window / 2.0
            left_edge = max(0, current_time - half_window)
            right_edge = min(duration, left_edge + zoom_window)

            # Re-adjust left constraint if hitting the right track wall
            if right_edge == duration:
                left_edge = max(0, duration - zoom_window)

            ax2.set_xlim(left_edge, right_edge)

        # Print streaming playhead coordinates to terminal
        zoom_status = "[ZOOMED]" if is_zoomed else "[FULL]"
        sys.stdout.write(
            f"\r{zoom_status} Playhead Position: {current_time:.3f}s"
        )
        sys.stdout.flush()
    else:
        pygame.mixer.music.play()

    return playhead1, playhead2


# Configure Matplotlib to refresh the playhead frame at 60 FPS
# Note: blit=False is used here to allow the background x-axis ticks to refresh smoothly during zoom scrolling
ani = animation.FuncAnimation(
    fig,
    update_playhead,
    init_func=init_playback,
    blit=False,
    interval=16,
    cache_frame_data=False,
)

# Open the GUI and start everything
while True:
    plt.show()

# Clean up audio channels when closing the window
pygame.mixer.music.stop()
pygame.mixer.quit()
print("\nDAW Session Closed.")
