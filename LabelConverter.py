"""
- LabelConverter -

This program merges a bundle of label files in .txt format associated 
with specific video files into unified .csv files. 

Features:
- Users can select multiple video files as input.
- Corresponding label folders are identified and processed automatically.
- Output CSV files are generated with the processed label data.
- A graphical user interface (GUI) built with Tkinter enables user-friendly operation.
- Real-time progress tracking is displayed during the processing of files.

Workflow:
1. Select input video files.
2. Specify the folder containing corresponding label files.
3. Choose an output directory for the generated CSV files.
4. Process the files and track progress in the GUI.

"""

import os, cv2, tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

def ProcessFiles(video_paths: list, label_paths: list, output_folder: str):
    """
    The ProcessFiles function processes label files associated with the 
    given video files and saves them as CSV files.

    Args:
        video_paths (list of str):
            A list of file paths to input video files.
        label_paths (list of Path):
            A list of directories containing label files.
        output_folder (str):
            The path to the directory where processed CSV files will be saved.

    Returns:
        None
    """
    # Hide start and close buttons and show the progress bar and label
    start_button.grid_remove()
    close_button.grid_remove()
    progress_bar.grid(row=6, column=1, padx=10, pady=10, sticky="ew")
    progress_label.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

    for video_path in video_paths:
        video_name = Path(video_path).stem  # Extract the video name (stem) from the file path
        # Find label directories matching the video name
        video_label_paths = [label_path for label_path in label_paths if video_name in str(label_path)]
        # Calculate the total number of label files for progress tracking
        total_video_files = sum(len(list(label_path.iterdir())) for label_path in video_label_paths)
        progress_bar["maximum"] = total_video_files
        video_file_count = 0

        # Get the dimensions of the video
        try:
            video = cv2.VideoCapture(video_path)
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video.release()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read video dimensions for {video_name}: {e}")
            return

        for label_path in video_label_paths:
            try:
                # List all label files in the directory
                unsorted_txt_files = [file.name for file in label_path.iterdir()]
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open the files in {label_path}: {e}")
                continue

            # Sort the label files by the numeric value in their names
            txt_files = sorted(unsorted_txt_files, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[-1]))

            # Define the output CSV file path
            output_file = os.path.join(output_folder, "_".join(str(label_path).split("\\")[-1].split("_")[:-1]) + ".csv")

            try:
                with open(output_file, 'wt', encoding='utf-8') as csv_file:
                    # Write the header row to the CSV file
                    column_names = [
                        'track', 'frame_idx', 'instance_score', 'Nose.x', 'Nose.y', 'Nose.score',
                        'Body_C.x', 'Body_C.y', 'Body_C.score', 'Tail.x', 'Tail.y', 'Tail.score',
                        'Ear_L.x', 'Ear_L.y', 'Ear_L.score', 'Ear_R.x', 'Ear_R.y', 'Ear_R.score'
                    ]
                    csv_file.write(','.join(column_names))
                    csv_file.write("\n")

                    for file_path in txt_files:
                        frame_idx = file_path.split("_")[-1].split(".")[0]  # Extract the frame index from the file name

                        try:
                            with open(str(label_path) + "\\" + file_path, 'rt', encoding='utf-8') as file:
                                content = file.read()  # Read the label file contents
                                rows = sorted(content.split("\n")[:-1])  # Split into rows and sort them

                                for row in rows:
                                    row = row.split(" ")  # Split each row into columns
                                    # Modify the row to include additional details
                                    edited_row = row[:1] + [frame_idx, '0.9'] + row[5:]
                                    edited_row[0] = 'track_' + edited_row[0]  # Add a prefix to the track ID

                                    # Scale the x and y coordinates based on the video dimensions
                                    for i in range(3, 18, 3):
                                        edited_row[i] = str(float(edited_row[i]) * width)
                                        edited_row[i + 1] = str(float(edited_row[i + 1]) * height)

                                    # Write the processed row to the CSV file
                                    csv_file.write(','.join(edited_row))
                                    csv_file.write("\n")
                        except Exception as e:
                            messagebox.showerror("Error", f"Error in processing file {file_path}: {e}")

                        # Update the progress bar and label
                        video_file_count += 1
                        progress_bar["value"] = video_file_count
                        processing_text.set(f"Processing {video_name}: {video_file_count}/{total_video_files}")
                        root.update_idletasks()

            except Exception as e:
                messagebox.showerror("Error", f"Error in opening the result file: {e}")

    # Restore the initial state of the GUI after processing
    progress_bar.grid_remove()
    progress_label.grid_remove()
    start_button.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
    close_button.grid(row=6, column=2, padx=10, pady=10, sticky="ew")

    # Show a success message
    messagebox.showinfo("Success", "All processes completed successfully!")

class LabelConverterGUI:
    """
    A GUI class for converting label files associated with video files into CSV format.

    This class provides a graphical user interface for users to:
    - Select input video files.
    - Find and select corresponding label folders.
    - Specify an output folder for the converted CSV files.
    - Display progress during the processing of files.

    Attributes:
        root (tk.Tk):
            The root window of the Tkinter GUI.

        video_frame (tk.Frame):
            Frame containing the input video entry and scrollbars.

        video_entry (tk.Text):
            Text box for displaying selected video file paths.

        video_scroll_x (tk.Scrollbar):
            Horizontal scrollbar for the video entry box.

        video_scroll_y (tk.Scrollbar):
            Vertical scrollbar for the video entry box.

        label_frame (tk.Frame):
            Frame containing the label folder list and scrollbars.

        label_folder_list (tk.Listbox):
            Listbox for displaying selected label folder paths.

        label_scroll_x (tk.Scrollbar):
            Horizontal scrollbar for the label folder list.

        label_scroll_y (tk.Scrollbar):
            Vertical scrollbar for the label folder list.

        output_frame (tk.Frame):
            Frame containing the output folder entry and scrollbars.

        output_entry (tk.Text):
            Text box for displaying the selected output folder path.

        output_scroll_x (tk.Scrollbar):
            Horizontal scrollbar for the output entry box.
    """

    def __init__(self, root):
        """
        Initializes the LabelConverterGUI with the given Tkinter root window.

        Args:
            root (tk.Tk):
                The root window of the Tkinter GUI.
        """
        self.root = root  # Assign the root window
        self.root.title("Label File Processor")  # Set the title of the GUI window
        self.root.minsize(820, 200)  # Set minimum size of the window

        # Configure resizing behavior for grid layout
        self.root.columnconfigure(1, weight=1)  # Allow column 1 to expand horizontally
        self.root.rowconfigure(0, weight=1)  # Allow row 0 to expand vertically
        self.root.rowconfigure(2, weight=1)  # Allow row 2 to expand vertically

        # Input Videos Section
        video_label = tk.Label(self.root, text="Input Videos:", font=("Arial", 10))  # Label for input videos
        video_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")  # Place label in grid

        self.video_frame = tk.Frame(self.root)  # Frame to hold video entry and scrollbars
        self.video_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  # Place frame in grid

        self.video_entry = tk.Text(self.video_frame, wrap="none", height=1, font=("Arial", 10))  # Text box for video paths
        self.video_entry.pack(side="left", fill="both", expand=True)  # Pack text box in frame

        self.video_scroll_y = tk.Scrollbar(self.video_frame, orient="vertical", command=self.video_entry.yview)  # Vertical scrollbar
        self.video_scroll_y.pack_forget()  # Initially hidden

        self.video_entry.configure(yscrollcommand=self.video_scroll_y.set)  # Link scrollbar to text box

        self.video_scroll_x = tk.Scrollbar(self.root, orient="horizontal", command=self.video_entry.xview)  # Horizontal scrollbar
        self.video_scroll_x.grid_remove()  # Initially hidden

        self.video_entry.configure(xscrollcommand=self.video_scroll_x.set)  # Link scrollbar to text box

        video_button = tk.Button(self.root, text="Browse", command=self.select_videos, font=("Arial", 10))  # Button to browse videos
        video_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")  # Place button in grid

        # Label Folders Section
        label_folder_label = tk.Label(self.root, text="Label Folders:", font=("Arial", 10))  # Label for label folders
        label_folder_label.grid(row=2, column=0, padx=10, pady=10, sticky="nw")  # Place label in grid

        self.label_frame = tk.Frame(self.root)  # Frame to hold label folder list and scrollbars
        self.label_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")  # Place frame in grid

        self.label_folder_list = tk.Listbox(self.label_frame, selectmode=tk.MULTIPLE, height=1, font=("Arial", 10))  # Listbox for folder paths
        self.label_folder_list.pack(side="left", fill="both", expand=True)  # Pack listbox in frame

        self.label_scroll_y = tk.Scrollbar(self.label_frame, orient="vertical", command=self.label_folder_list.yview)  # Vertical scrollbar
        self.label_scroll_y.pack_forget()  # Initially hidden

        self.label_folder_list.configure(yscrollcommand=self.label_scroll_y.set)  # Link scrollbar to listbox

        self.label_scroll_x = tk.Scrollbar(self.root, orient="horizontal", command=self.label_folder_list.xview)  # Horizontal scrollbar
        self.label_scroll_x.grid_remove()  # Initially hidden

        self.label_folder_list.configure(xscrollcommand=self.label_scroll_x.set)  # Link scrollbar to listbox

        add_folder_button = tk.Button(self.root, text="Find Folders", command=self.select_label_folders, font=("Arial", 10))  # Button to find folders
        add_folder_button.grid(row=2, column=2, padx=10, pady=5, sticky="ne")  # Place button in grid

        # Output Folder Section
        output_label = tk.Label(self.root, text="Output Folder:", font=("Arial", 10))  # Label for output folder
        output_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")  # Place label in grid

        self.output_frame = tk.Frame(self.root)  # Frame to hold output folder entry and scrollbars
        self.output_frame.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")  # Place frame in grid

        self.output_entry = tk.Text(self.output_frame, wrap="none", height=1, font=("Arial", 10))  # Text box for output folder path
        self.output_entry.pack(side="left", fill="both", expand=True)  # Pack text box in frame

        self.output_scroll_x = tk.Scrollbar(self.root, orient="horizontal", command=self.output_entry.xview)  # Horizontal scrollbar
        self.output_scroll_x.grid_remove()  # Initially hidden

        self.output_entry.configure(xscrollcommand=self.output_scroll_x.set)  # Link scrollbar to text box

        output_button = tk.Button(self.root, text="Browse", command=self.select_output_folder, font=("Arial", 10))  # Button to browse output folder
        output_button.grid(row=4, column=2, padx=10, pady=10, sticky="ew")  # Place button in grid

        # Progress Label
        global processing_text
        processing_text = tk.StringVar()  # StringVar to update progress label
        global progress_label
        progress_label = tk.Label(self.root, textvariable=processing_text, font=("Arial", 10))  # Label to show processing status
        progress_label.grid_remove()  # Initially hidden

        # Progress Bar
        global progress_bar
        progress_bar = Progressbar(self.root, orient="horizontal", mode="determinate")  # Progress bar
        progress_bar.grid_remove()  # Initially hidden

        # Process Button
        global start_button
        start_button = tk.Button(self.root, text="Process", command=self.start_processing, font=("Arial", 10))  # Button to start processing
        start_button.grid(row=6, column=0, padx=10, pady=10, sticky="ew")  # Place button in grid

        # Close Button
        global close_button
        close_button = tk.Button(self.root, text="Close", command=self.root.destroy, font=("Arial", 10))  # Button to close the application
        close_button.grid(row=6, column=2, padx=10, pady=10, sticky="ew")  # Place button in grid

    def select_videos(self):
        """
        Opens a file dialog for the user to select input video files and updates the video entry text box.
        """
        video_paths = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])  # Open file dialog
        if video_paths:
            self.video_entry.delete("1.0", tk.END)  # Clear current text
            self.video_entry.insert("1.0", "\n".join(video_paths))  # Insert selected paths
            self.video_scroll_x.grid(row=1, column=1, padx=10, pady=10, sticky="ew")  # Show horizontal scrollbar
            self.video_scroll_y.pack(side="right", fill="y")  # Show vertical scrollbar

    def select_label_folders(self):
        """
        Opens a directory dialog for the user to select the parent folder containing label folders.
        Updates the label folder list with matching folders.
        """
        video_names = [Path(v).stem for v in self.video_entry.get("1.0", tk.END).strip().split("\n")]  # Get video names
        parent_folder = filedialog.askdirectory(title="Select Parent Folder Containing Label Folders")  # Open directory dialog
        if parent_folder:
            label_paths = [
                Path(os.path.join(parent_folder, folder))
                for folder in os.listdir(parent_folder)
                if any(video_name in folder for video_name in video_names) and os.path.isdir(os.path.join(parent_folder, folder))
            ]

            if not label_paths:
                messagebox.showerror("Error", "No matching label folders found for the selected videos.")  # Show error if no matches
                return

            self.label_folder_list.delete(0, tk.END)  # Clear current list
            for path in label_paths:
                self.label_folder_list.insert(tk.END, str(path))  # Add matching folders

            self.label_scroll_x.grid(row=3, column=1, padx=10, pady=10, sticky="ew")  # Show horizontal scrollbar
            self.label_scroll_y.pack(side="right", fill="y")  # Show vertical scrollbar

    def select_output_folder(self):
        """
        Opens a directory dialog for the user to select the output folder and updates the output entry text box.
        """
        output_folder = filedialog.askdirectory()  # Open directory dialog
        if output_folder:
            self.output_entry.delete("1.0", tk.END)  # Clear current text
            self.output_entry.insert("1.0", output_folder)  # Insert selected path
            self.output_scroll_x.grid(row=5, column=1, padx=10, pady=10, sticky="ew")  # Show horizontal scrollbar

    def start_processing(self):
        """
        Starts the label file processing workflow based on the user's inputs.
        Validates inputs and calls the processing function.
        """
        video_paths = self.video_entry.get("1.0", tk.END).strip().split("\n")  # Get video paths from text box
        output_folder = self.output_entry.get("1.0", tk.END).strip()  # Get output folder path
        label_paths = [Path(self.label_folder_list.get(idx)) for idx in range(self.label_folder_list.size())]  # Get selected label folder paths

        if not video_paths or not label_paths or not output_folder:
            messagebox.showerror("Error", "Please select videos, label folders, and an output folder.")  # Validate inputs
            return

        ProcessFiles(video_paths, label_paths, output_folder)  # Call the processing function

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelConverterGUI(root)
    root.mainloop()