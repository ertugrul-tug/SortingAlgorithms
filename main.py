import wx
import wx.lib.colourdb
import pygame
import pygame.midi as midi
import random
import time
import threading
import math

# Create a dictionary to map values to MIDI notes
value_to_note = {
    0: 60,  # C4
    1: 62,  # D4
    2: 64,  # E4
    # Add more mappings as needed
}

# Initialize the MIDI output
midi.init()
player = midi.Output(0)


class SortingFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Sorting Algorithms Visualization")
        self.SetSize((1000, 740))  # Set the initial window size
        self.Center()  # Center the window on the screen

        self.sorting_thread = None
        self.speed = None
        self.algorithm = None
        self.algorithm_name = None
        self.numbers = None
        self.initial_numbers = None
        self.completed = 0
        self.print_result = ""
        self.complexity_result = ""
        self.complexity_type_result = ""
        self.comparison_count = 0

        self.panel = wx.Panel(self)

        # State of the program
        self.state = 0

        # Sorting algorithms
        self.algorithms = {
            "Bubble Sort": self.bubble_sort,
            "Selection Sort": self.selection_sort,
            "Quick Sort": self.quick_sort,
            "Insertion Sort": self.insertion_sort,
            "Merge Sort": self.merge_sort
        }

        # Graph panel
        self.graph_panel = GraphPanel(self.panel)

        # Size options
        self.size_label = wx.StaticText(self.panel, label="Size:")
        self.random_size_slider = wx.Slider(self.panel, value=100, minValue=10, maxValue=500, style=wx.SL_HORIZONTAL)

        # Speed option
        self.speed_label = wx.StaticText(self.panel, label="Speed:")
        self.speed_slider = wx.Slider(self.panel, value=50, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL)

        # Sorting algorithms list box
        self.algorithms_radiobox = wx.RadioBox(self.panel, choices=list(self.algorithms.keys()),
                                               style=wx.RA_SPECIFY_ROWS)

        # Graph types radio buttons
        self.graph_type_label = wx.StaticText(self.panel, label="Graph Type:")
        self.graph_type_radiobox = wx.RadioBox(self.panel,
                                               choices=["Scatter Chart", "Column (Bar) Graph", "Stem Graph"],
                                               style=wx.RA_SPECIFY_ROWS)

        # Create, Start, Stop, Reset buttons
        self.button_create = wx.Button(self.panel, wx.ID_ANY, "Create")
        self.button_start = wx.Button(self.panel, wx.ID_ANY, "Start")
        self.button_stop = wx.Button(self.panel, wx.ID_ANY, "Stop")
        self.button_reset = wx.Button(self.panel, wx.ID_ANY, "Reset")

        # Box for array inputs
        self.array_label = wx.StaticText(self.panel, label="Enter your numbers here with , in between:")
        self.array_text = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)

        # Bind event handlers
        self.Bind(wx.EVT_BUTTON, self.on_create, self.button_create)
        self.Bind(wx.EVT_BUTTON, self.on_start, self.button_start)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        self.Bind(wx.EVT_BUTTON, self.on_reset, self.button_reset)


        # Box for the result of comparisons and complexity analysis
        self.comparison_label = wx.StaticText(self.panel, label="Comparisons Count:")
        self.comparison_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        self.complexity_type = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        self.complexity_label = wx.StaticText(self.panel, label="Complexity:")
        self.complexity_text = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        self.comparison_text.SetMinSize(wx.Size(560, -1))
        self.complexity_type.SetMinSize(wx.Size(673, -1))
        self.complexity_text.SetMinSize(wx.Size(606, -1))

        # Sizer for left side elements
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.size_label, 0, wx.ALL, 5)
        left_sizer.Add(self.random_size_slider, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.speed_label, 0, wx.ALL, 5)
        left_sizer.Add(self.speed_slider, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.algorithms_radiobox, 1, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.graph_type_label, 0, wx.ALL, 5)
        left_sizer.Add(self.graph_type_radiobox, 0, wx.ALL, 5)
        left_sizer.Add(self.button_create, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.button_start, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.button_stop, 0, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(self.button_reset, 0, wx.EXPAND | wx.ALL, 5)

        # Sizer for the graph
        graph_sizer = wx.BoxSizer(wx.HORIZONTAL)
        graph_sizer.Add(left_sizer, 0, wx.EXPAND | wx.ALL, 10)
        graph_sizer.Add(self.graph_panel, 1, wx.EXPAND | wx.ALL, 10)

        # Sizer for user given array
        array_sizer = wx.BoxSizer(wx.HORIZONTAL)
        array_sizer.Add(self.array_label, 0, wx.ALL, 5)
        array_sizer.Add(self.array_text, 0, wx.EXPAND | wx.ALL, 5)

        # Sizer for the comparison
        results_sizer = wx.BoxSizer(wx.HORIZONTAL)
        results_sizer.Add(self.comparison_label, 0, wx.EXPAND | wx.ALL, 2)
        results_sizer.Add(self.comparison_text, 0, wx.EXPAND | wx.ALL, 2)

        # Sizer for the complexity type
        complexity_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        complexity_type_sizer.Add(self.complexity_type, 0, wx.EXPAND | wx.ALL, 2)

        # Sizer for the complexity
        complexity_sizer = wx.BoxSizer(wx.HORIZONTAL)
        complexity_sizer.Add(self.complexity_label, 0, wx.EXPAND | wx.ALL, 2)
        complexity_sizer.Add(self.complexity_text, 0, wx.EXPAND | wx.ALL, 2)

        # Main sizer for the frame
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(array_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(graph_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(results_sizer, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(complexity_type_sizer, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(complexity_sizer, 0, wx.EXPAND | wx.ALL, 2)

        # Activate or Disable buttons accordingly
        self.button_create.Enable()
        self.button_start.Disable()
        self.button_stop.Disable()
        self.button_reset.Disable()

        self.panel.SetSizer(main_sizer)
        self.Layout()

    def perform_complexity_analysis(self):
        if self.algorithm_name == "Bubble Sort":
            self.complexity_type.SetValue("Bubble Sort has a worst-case time complexity of O(n^2) and a best-case time complexity of Ω(n).")
        elif self.algorithm_name == "Insertion Sort":
            self.complexity_type.SetValue("Insertion Sort has a worst-case time complexity of O(n^2) and a best-case time complexity of Ω(n).")
        elif self.algorithm_name == "Selection Sort":
            self.complexity_type.SetValue("Selection Sort has a worst-case time complexity of O(n^2) and a best-case time complexity of Ω(n^2).")
        elif self.algorithm_name == "Merge Sort":
            self.complexity_type.SetValue("Merge Sort has a worst-case time complexity of O(n log n) and a best-case time complexity of Ω(n log n).")
        elif self.algorithm_name == "Quick Sort":
            self.complexity_type.SetValue("Quick Sort has a worst-case time complexity of O(n^2) and a best-case time complexity of Ω(n log n).")
        elif self.algorithm_name == "Heap Sort":
            self.complexity_type.SetValue("Heap Sort has a worst-case time complexity of O(n log n) and a best-case time complexity of Ω(n log n).")
        else:
            self.complexity_type.SetValue("Complexity analysis is not available for the selected algorithm.")
        self.on_complexity_analysis()

    def update_comparison_text(self):
        self.comparison_count += 1
        self.comparison_text.SetValue(f"{self.comparison_count}")

    def on_complexity_analysis(self):
        n = len(self.numbers)
        if self.algorithm_name == "Bubble Sort":
            self.complexity_text.SetValue(f"Worst-case time complexity: O({n*n}) Best-case time complexity of Ω({n}).")
        elif self.algorithm_name == "Insertion Sort":
            self.complexity_text.SetValue(f"Worst-case time complexity: O({n*n}) Best-case time complexity of Ω({n}).")
        elif self.algorithm_name == "Selection Sort":
            self.complexity_text.SetValue(f"Worst-case time complexity: O({n*n}) Best-case time complexity of Ω({n*n}).")
        elif self.algorithm_name == "Merge Sort":
            self.complexity_text.SetValue(f"Worst-case time complexity: O({n*math.log(n)}) Best-case time complexity of Ω({n*math.log(n)}).")
        elif self.algorithm_name == "Quick Sort":
            self.complexity_text.SetValue(f"Worst-case time complexity: O({n*n}) Best-case time complexity of Ω({n*math.log(n)}).")
        elif self.algorithm_name == "Heap Sort":
            self.complexity_text.SetValue(f"Worst-case time complexity: O({n*math.log(n)}) Best-case time complexity of Ω({n*math.log(n)}).")
        else:
            self.complexity_text.SetValue("")

    def on_input_enter(self):
        # Get the input text
        input_text = self.input_text.GetValue()

        # Split the input text using the special character separator
        numbers = input_text.split(",")

        # Convert the numbers from strings to integers
        numbers = [int(num) for num in numbers]

        # Set the numbers in the graph panel and update the displayed graph
        self.graph_panel.set_numbers(numbers)
        self.graph_panel.Refresh()


    def on_create(self, event):
        graph_type = self.graph_type_radiobox.GetStringSelection()

        size = self.random_size_slider.GetValue()
        self.numbers = random.sample(range(1, size + 1), size)

        self.graph_panel.set_numbers(self.numbers)
        self.graph_panel.set_graph_type(graph_type)

        if not self.numbers:
            wx.MessageBox("No data to sort!", "Error", wx.OK | wx.ICON_ERROR)
            return

        algorithm_index = self.algorithms_radiobox.GetSelection()

        if algorithm_index == wx.NOT_FOUND:
            wx.MessageBox("No algorithm chosen!", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.algorithm_name = self.algorithms_radiobox.GetString(algorithm_index)
        self.algorithm = self.algorithms[self.algorithm_name]
        self.speed = (101 - self.speed_slider.GetValue()) / 1000

        # Activate or Disable buttons accordingly
        self.button_create.Disable()
        self.button_start.Enable()
        self.button_stop.Disable()
        self.button_reset.Enable()

        # Activate or Disable selections accordingly
        self.graph_type_radiobox.Disable()
        self.algorithms_radiobox.Disable()
        self.speed_slider.Disable()
        self.random_size_slider.Disable()

        self.perform_complexity_analysis()

        self.initial_numbers = self.numbers
        self.sorting_thread = threading.Thread(target=self.algorithm, args=(self.speed,))
        self.comparison_count = 0
        self.completed = 0
        self.state = 1

    def on_start(self, event):
        if self.sorting_thread and self.sorting_thread.is_alive():
            # Sorting thread is already running, do nothing
            return

        # Activate or Disable buttons accordingly
        self.button_create.Disable()
        self.button_start.Disable()
        self.button_stop.Enable()
        self.button_reset.Disable()

        # Activate or Disable selections accordingly
        self.graph_type_radiobox.Disable()
        self.algorithms_radiobox.Disable()
        self.speed_slider.Disable()
        self.random_size_slider.Disable()

        self.state = 2

        if self.completed == 0:
            # Sorting thread exists but has not completed
            self.sorting_thread = threading.Thread(target=self.algorithm, args=(self.speed,))
            self.sorting_thread.start()
        else:
            # Sorting thread does not exist, create a new one
            self.sorting_thread = threading.Thread(target=self.algorithm, args=(self.speed,))
            self.sorting_thread.start()

    def on_stop(self, event):
        if self.sorting_thread and self.sorting_thread.is_alive():
            self.sorting_thread = None

        # Activate or Disable buttons accordingly
        self.button_create.Disable()
        self.button_start.Enable()
        self.button_stop.Disable()
        self.button_reset.Enable()

        # Activate or Disable selections accordingly
        self.graph_type_radiobox.Disable()
        self.algorithms_radiobox.Disable()
        self.speed_slider.Disable()
        self.random_size_slider.Disable()

        self.state = 3

    def on_reset(self, event):

        self.state = 0
        self.numbers = self.initial_numbers
        self.graph_panel.set_numbers(self.numbers)
        self.graph_panel.set_highlighted_indices([])

        # Activate or Disable buttons accordingly
        self.button_create.Enable()
        self.button_start.Enable()
        self.button_stop.Disable()
        self.button_reset.Disable()

        # Activate or Disable selections accordingly
        self.graph_type_radiobox.Enable()
        self.algorithms_radiobox.Enable()
        self.speed_slider.Enable()
        self.random_size_slider.Enable()

        # Reset the count
        self.comparison_count = 0

    def on_complete(self, numbers):
        self.state = 0

        # Set the final sorted numbers and reset the highlighted indices
        self.graph_panel.set_numbers(numbers)
        self.graph_panel.set_highlighted_indices([])
        self.completed = 1

        # Activate or Disable buttons accordingly
        self.button_create.Enable()
        self.button_start.Disable()
        self.button_stop.Disable()
        self.button_reset.Enable()

        # Activate or Disable selections accordingly
        self.graph_type_radiobox.Enable()
        self.algorithms_radiobox.Enable()
        self.speed_slider.Enable()
        self.random_size_slider.Enable()

    def bubble_sort(self, speed):
        numbers = self.numbers.copy()
        n = len(numbers)
        if self.state == 2:
            for i in range(n):
                # Flag to check if any swaps were made in this pass
                swapped = False

                for j in range(n - i - 1):
                    if numbers[j] > numbers[j + 1]:
                        numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
                        self.graph_panel.set_highlighted_indices([j, j + 1])
                        self.graph_panel.Refresh()  # Update the panel
                        time.sleep(speed)
                        self.graph_panel.set_numbers(numbers)  # Set the current state of numbers
                        swapped = True

                    if self.state == 3:
                        self.numbers = numbers
                        return
                    self.update_comparison_text()
                # If no swaps were made in this pass, the list is already sorted
                if not swapped:
                    break

            self.on_complete(numbers)

    def selection_sort(self, speed):
        numbers = self.numbers.copy()
        n = len(numbers)
        i = 0
        j = 0

        while i < n - 1:
            min_idx = i
            j = i + 1

            while j < n:
                if numbers[j] < numbers[min_idx]:
                    min_idx = j
                    self.update_comparison_text()

                j += 1

            if self.state == 3:
                self.numbers = numbers
                return

            numbers[i], numbers[min_idx] = numbers[min_idx], numbers[i]
            self.graph_panel.set_highlighted_indices([i, min_idx])
            self.graph_panel.Refresh()
            time.sleep(speed)
            self.graph_panel.set_numbers(numbers)

            i += 1

        self.on_complete(numbers)

    def insertion_sort(self, speed):
        numbers = self.numbers.copy()
        n = len(numbers)
        i = 1

        while i < n:
            key = numbers[i]
            j = i - 1

            while j >= 0 and numbers[j] > key:
                numbers[j + 1] = numbers[j]
                self.update_comparison_text()
                self.graph_panel.set_highlighted_indices([j, j + 1])
                self.graph_panel.Refresh()
                time.sleep(speed)
                self.graph_panel.set_numbers(numbers)
                j -= 1

                if self.state == 3:
                    self.numbers = numbers
                    return

            numbers[j + 1] = key
            self.update_comparison_text()
            self.graph_panel.set_highlighted_indices([])
            self.graph_panel.Refresh()
            time.sleep(speed)
            self.graph_panel.set_numbers(numbers)

            i += 1
        self.on_complete(numbers)

    def merge_sort(self, speed):
        numbers = self.numbers.copy()

        if self.state == 2:
            def merge(arr, l, m, r):
                if self.state == 3:
                    self.numbers = arr
                    return
                n1 = m - l + 1
                n2 = r - m

                L = [0] * n1
                R = [0] * n2

                for i in range(n1):
                    L[i] = arr[l + i]
                    self.update_comparison_text()

                for j in range(n2):
                    R[j] = arr[m + 1 + j]
                    self.update_comparison_text()

                i = j = 0
                k = l

                while i < n1 and j < n2:
                    if L[i] <= R[j]:
                        arr[k] = L[i]
                        self.update_comparison_text()
                        i += 1
                    else:
                        arr[k] = R[j]
                        self.update_comparison_text()
                        j += 1

                    k += 1

                    if self.state == 3:
                        self.numbers = arr
                        return

                    self.graph_panel.set_highlighted_indices([l + i, m + 1 + j])
                    self.graph_panel.set_numbers(arr)
                    self.graph_panel.Refresh()
                    time.sleep(speed)

                while i < n1:
                    arr[k] = L[i]
                    self.update_comparison_text()
                    i += 1
                    k += 1

                while j < n2:
                    arr[k] = R[j]
                    self.update_comparison_text()
                    j += 1
                    k += 1

                # Set the correct indices in the original array
                for idx in range(l, r + 1):
                    self.graph_panel.set_highlighted_indices([idx])
                    self.graph_panel.Refresh()
                    time.sleep(speed)

            def merge_sort_helper(arr, l, r):
                if self.state == 3:
                    self.numbers = arr
                    return
                if l < r:
                    m = (l + r) // 2
                    merge_sort_helper(arr, l, m)
                    merge_sort_helper(arr, m + 1, r)
                    merge(arr, l, m, r)
                    self.update_comparison_text()
                    self.numbers = arr
                    self.graph_panel.set_numbers(arr)
                    self.graph_panel.Refresh()
                    time.sleep(speed)

            merge_sort_helper(numbers, 0, len(numbers) - 1)

            if self.state == 3:
                return
            else:
                self.on_complete(numbers)

    def quick_sort(self, speed):
        numbers = self.numbers.copy()

        if self.state == 2:
            def partition(arr, low, high):
                if self.state == 3:
                    self.numbers = arr
                    return
                i = (low - 1)
                pivot = arr[high]

                for j in range(low, high):
                    if arr[j] <= pivot:
                        i = i + 1
                        arr[i], arr[j] = arr[j], arr[i]
                        self.graph_panel.set_highlighted_indices([i, high, low, j])  # Highlight subarrays
                        self.graph_panel.set_numbers(arr)
                        time.sleep(speed)

                    self.update_comparison_text()

                    if self.state == 3:
                        self.numbers = arr
                        return -1

                arr[i + 1], arr[high] = arr[high], arr[i + 1]
                return (i + 1)

            def quick_sort_helper(arr, low, high):
                if self.state == 3:
                    self.numbers = arr
                    return
                if low < high:
                    pi = partition(arr, low, high)
                    if pi == -1:
                        return
                    quick_sort_helper(arr, low, pi - 1)
                    quick_sort_helper(arr, pi + 1, high)
                    self.update_comparison_text()
                    self.graph_panel.set_highlighted_indices([pi + 1, high, low, pi - 1])  # Highlight subarrays
                    self.graph_panel.set_numbers(arr)
                    self.graph_panel.Refresh()
                    time.sleep(speed)

            quick_sort_helper(numbers, 0, len(numbers) - 1)

            self.on_complete(numbers)


class GraphPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.numbers = []
        self.highlighted_indices = []
        self.gradient_colors = []
        self.graph_type = "Scatter Chart"

        self.Bind(wx.EVT_PAINT, self.on_paint)

        # Initialize the gradient colors
        self.initialize_gradient_colors()

    def initialize_gradient_colors(self):
        wx.lib.colourdb.updateColourDB()
        if self.graph_type == "Stem Graph":  # To see the graph better swap the colors
            min_color = wx.Colour(0, 255, 255)  # Cyan
            max_color = wx.Colour(0, 0, 128)  # Dark Blue
        else:
            min_color = wx.Colour(0, 0, 128)  # Dark Blue
            max_color = wx.Colour(0, 255, 255)  # Cyan

        if not self.numbers:  # Check if the numbers list is empty
            return

        # Get the RGB values for the minimum and maximum colors
        min_r, min_g, min_b = min_color.Red(), min_color.Green(), min_color.Blue()
        max_r, max_g, max_b = max_color.Red(), max_color.Green(), max_color.Blue()

        # Determine the number of steps in the gradient based on the range of values
        num_steps = max(max(self.numbers) - min(self.numbers), 1)

        # Calculate the step size for each RGB channel
        r_step = (max_r - min_r) / num_steps
        g_step = (max_g - min_g) / num_steps
        b_step = (max_b - min_b) / num_steps

        # Generate the gradient colors
        self.gradient_colors = []
        for num in self.numbers:
            # Calculate the RGB values for the current number based on its position in the range
            r = max_r - int((num - min(self.numbers)) * r_step)
            g = max_g - int((num - min(self.numbers)) * g_step)
            b = max_b - int((num - min(self.numbers)) * b_step)

            self.gradient_colors.append(wx.Colour(r, g, b))

    def set_numbers(self, numbers):
        self.numbers = numbers
        self.initialize_gradient_colors()
        self.Refresh()

    def set_highlighted_indices(self, indices):
        self.highlighted_indices = indices
        for index in self.highlighted_indices:
            if index < len(self.numbers):
                value = self.numbers[index]
                self.play_note_by_value(value)
        self.Refresh()

    def play_note_by_value(self, value):
        if value not in value_to_note:
            # Generate a new MIDI note based on the value
            note = 0 + value  # Adjust the offset as needed
            value_to_note[value] = note

        note = value_to_note[value]
        self.play_note(note)

    def play_note(self, note):
        player.note_on(note, 127)  # Play the note with maximum velocity
        player.note_off(note)

    def set_graph_type(self, graph_type):
        self.graph_type = graph_type
        self.Refresh()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()

        width, height = self.GetSize()

        if not self.numbers:  # Check if the numbers list is empty
            return

        if self.graph_type == "Scatter Chart":
            self.draw_scatter_chart(dc, width, height)
        elif self.graph_type == "Column (Bar) Graph":
            self.draw_column_graph(dc, width, height)
        elif self.graph_type == "Stem Graph":
            self.draw_stem_graph(dc, width, height)

    def draw_scatter_chart(self, dc, width, height):
        for i, num in enumerate(self.numbers):
            x = int((i + 0.5) * width / len(self.numbers))
            y = int((1 - num / max(self.numbers)) * (height - 20))
            if i in self.highlighted_indices:
                dc.SetPen(wx.Pen(wx.BLACK))  # Set the outline color
                dc.SetBrush(wx.Brush(wx.RED))  # Set the fill color to red for highlighted indices
                dc.DrawCircle(x, y, 3)
            else:
                dc.SetPen(wx.Pen(wx.BLACK))  # Set the outline color
                dc.SetBrush(wx.Brush(self.gradient_colors[i]))  # Use gradient colors
                dc.DrawCircle(x, y, 3)

    def draw_column_graph(self, dc, width, height):
        num_columns = len(self.numbers)
        column_width = width // num_columns

        for i, num in enumerate(self.numbers):
            x = i * column_width
            column_height = int((num / max(self.numbers)) * (height - 20))

            if i in self.highlighted_indices:
                dc.SetPen(wx.Pen(wx.BLACK))  # Set the outline color
                dc.SetBrush(wx.Brush(wx.RED))  # Set the fill color to red for highlighted indices
                dc.DrawRectangle(x, height - column_height, column_width, column_height)
            else:
                dc.SetPen(wx.Pen(wx.BLACK))  # Set the outline color
                dc.SetBrush(wx.Brush(self.gradient_colors[i]))  # Use gradient colors
                dc.DrawRectangle(x, height - column_height, column_width, column_height)

    def draw_stem_graph(self, dc, width, height):
        for i, num in enumerate(self.numbers):
            x = int((i + 0.5) * width / len(self.numbers))
            stem_height = int((1 - num / max(self.numbers)) * (height - 20))
            if i in self.highlighted_indices:
                dc.SetPen(wx.Pen((wx.RED), width=2))  # Set the outline color
                dc.SetBrush(wx.Brush(wx.RED))  # Set the fill color to red for highlighted indices
                dc.DrawLine(x, height, x, height - stem_height)
            else:
                dc.SetPen(wx.Pen((self.gradient_colors[i]), width=2))  # Set the outline color
                dc.SetBrush(wx.Brush(self.gradient_colors[i]))  # Use gradient colors
                dc.DrawLine(x, height, x, height - stem_height)

    def __del__(self):
        player.close()
        midi.quit()


app = wx.App()
frame = SortingFrame()
frame.Show()
app.MainLoop()
