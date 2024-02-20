import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import webbrowser


class DrawBoxApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=500, height=900)
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

        self.remove_logo_button = tk.Button(master, text="Remove Logo", command=self.remove_logo)
        self.remove_logo_button.pack()

        self.segment_video()
        self.load_images()

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect_coords = None

    def segment_video(self):
        if not os.path.exists(self.snapshot_directory):
            os.makedirs(self.snapshot_directory)
        subprocess.run(["ffmpeg", "-i", "INPUT.mp4", "-vf", "fps=0.25", f"{self.snapshot_directory}/snapshot_%03d.png"])

    def load_images(self):
        for file in sorted(os.listdir(self.snapshot_directory)):
            if file.endswith(".png"):
                self.image_urls.append(os.path.join(self.snapshot_directory, file))

        self.show_image()

    def show_image(self):
        try:
            image_path = self.image_urls[self.current_image_index]
            image = Image.open(image_path)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        except Exception as e:
            print("Error loading image:", e)

    def next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_urls)
        self.show_image()

    def previous_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.image_urls)
        self.show_image()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)

    def on_move_press(self, event):
        if self.start_x and self.start_y:
            x, y = (event.x, event.y)
            if self.rect:
                self.canvas.delete(self.rect)
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline='red')

    def on_button_release(self, event):
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        x = min(event.x, self.start_x)
        y = min(event.y, self.start_y)
        self.rect_coords = (x, y, width, height)
        print("Coordinates:", x, y, width, height)

    def remove_logo(self):
        if self.rect_coords is None:
            print("No selection made.")
            return
        x, y, w, h = self.rect_coords
        input_file_path = 'INPUT.mp4'  # Replace with actual input file path
        output_file_path = './output/OUTPUT.mp4'  # Replace with actual output file path
        delogo_filter = f"delogo=x={x}:y={y}:w={w}:h={h}"
        command = ['ffmpeg', '-y', '-i', input_file_path, '-vf', delogo_filter, output_file_path]
        subprocess.run(command)
        
        
        print(f"Logo removed using coordinates: {self.rect_coords}")
        self.play_video(output_file_path)
        self.master.destroy()

    def play_video(self, video_path):
        try:
            subprocess.run(['xdg-open', video_path])
        except Exception as e:
            print(f"Error opening video: {e}")
        finally:
            webbrowser.open(video_path)


def main():
    root = tk.Tk()
    app = DrawBoxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
