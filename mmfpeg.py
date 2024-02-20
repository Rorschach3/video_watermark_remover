import subprocess


def remove_logo(input_file, output_file):
    delogo_filter = f'''delogo=
    x={x_horizontal}:
    y={y_vertical}:
    w={width}:
    h={height}'''
    command = ['ffmpeg', '-i', input_file, '-vf', delogo_filter, output_file]
    subprocess.run(command)


# Replace 'input_file_path' and 'output_file_path' with your desired file paths
input_file_path = 'instagram.mp4'
filename = input('File name: ')
output_file_path = f'./output/{filename}.mp4'
x_horizontal = input('Enter the x coordinate of the logo: ')
y_vertical = input('Enter the y coordinate of the logo: ')
width = input('Enter the width of the logo: ')
height = input('Enter the height of the logo: ')
remove_logo(input_file_path, output_file_path)
file = input('Name of file: ', '.mp4')
