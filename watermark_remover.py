import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import subprocess
import ffmpeg
import os
import sys


class WatermarkRemover:
    def __init__(self, master):
        self.master = master
        # window size
        self.canvas = tk.Canvas(master, width=680, height=920)
        self.canvas.pack()
        self.start_x, self.start_y = None, None
        self.rect = None
        self.image_urls = []
        self.snapshot_directory = "./snapshots"
        self.current_image_index = 0

        # Create Next and Previous buttons
        self.next_button = tk.Button(master, text="Next", command=self.next_image)
        self.next_button.pack(side=tk.RIGHT)
        self.prev_button = tk.Button(master, text="Previous", command=self.previous_image)
        self.prev_button.pack(side=tk.LEFT)

        self.remove_logo_button = tk.Button(master, text="Remove Watermark", command=self.remove_logo)
        self.remove_logo_button.pack()

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect_coords = None
        self.input = self.select_file()
        if self.input:
            self.segment_video()
            self.load_images()

    def select_file(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        if file_path:
            print("Selected file:", file_path)
        else:
            print("No file selected.")
        return file_path

    # split the video into screenshots
    def segment_video(self):
        if not os.path.exists(self.snapshot_directory):
            os.makedirs(self.snapshot_directory)
        # Notice change from `input` to `self.input`
        subprocess.run([
            "ffmpeg",
            "-i",
            self.input,
            "-vf",
            "fps=2",
            f"{self.snapshot_directory}/snapshot_%02d.png"
            ])

    # load images to canvas
    def load_images(self):
        for file in sorted(os.listdir(self.snapshot_directory)):
            if file.endswith(".png"):
                self.image_urls.append(os.path.join(self.snapshot_directory, file))

        self.show_image()

    # display image to canvas
    def show_image(self):
        try:
            image_path = self.image_urls[self.current_image_index]
            image = Image.open(image_path)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        except Exception as e:
            print("Error loading image:", e)

    def next_image(self):     # Add next image button
        self.current_image_index = (self.current_image_index + 1) % len(self.image_urls)
        self.show_image()

    def previous_image(self):  # Add previous image buttton
        self.current_image_index = (self.current_image_index - 1) % len(self.image_urls)
        self.show_image()

    def on_button_press(self, event):  # left mouse click erases previous rect
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)

    # draws red rect onto canvas
    def on_move_press(self, event):
        if self.start_x and self.start_y:
            x, y = (event.x, event.y)
            if self.rect:
                self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline='red')

    # on left mouse release, saves coordinates of rect
    def on_button_release(self, event):
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        x = min(event.x, self.start_x)
        y = min(event.y, self.start_y)
        self.rect_coords = (x, y, width, height)
        print("Coordinates:", x, y, width, height)

    # removes watermark/logo from masked area

    def remove_logo(self):
        if self.rect_coords is None:
            print("No selection made.")
            return
        x, y, w, h = self.rect_coords
        input_file_path = self.input
        output_file_path = './OUTPUT.mp4'
        delogo_filter = f"delogo=x={x}:y={y}:w={w}:h={h}"
        command = ['ffmpeg', '-y', '-i', input_file_path, '-vf', delogo_filter, output_file_path]
        subprocess.run(command)

        print(f"Logo removed using coordinates: {self.rect_coords}")
        print("Video watermark removed successfully!")
        self.master.destroy()
        

def main():
    root = tk.Tk()
    app = WatermarkRemover(root)
    root.mainloop()


if __name__ == "__main__":
    main()
