# filename: cellular_automata_art.py

import numpy as np
import matplotlib.pyplot as plt
import cv2
import os

# Cellular automata rules
def rules(x):
    return 0 if x < 2 else 1 if x == 2 or x == 3 else 0

# Initialize automata
automata = np.random.choice([0, 1], size=(100, 100))

# Create directory for frames
if not os.path.exists('frames'):
    os.makedirs('frames')

# Generate frames
for i in range(100):
    plt.imshow(automata)
    plt.axis('off')
    plt.savefig(f'frames/frame_{i:03d}.png')
    automata = np.pad(automata, 1)
    automata = np.array([[rules(np.sum(automata[i-1:i+2, j-1:j+2])) for j in range(1, automata.shape[1]-1)] for i in range(1, automata.shape[0]-1)])

# Compile frames into video
frames = []
for i in range(100):
    frames.append(cv2.imread(f'frames/frame_{i:03d}.png'))
height, width, layers = frames[0].shape
video = cv2.VideoWriter('art.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))
for frame in frames:
    video.write(frame)
video.release()

# Clean up frames
for i in range(100):
    os.remove(f'frames/frame_{i:03d}.png')
os.rmdir('frames')