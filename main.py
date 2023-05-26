import wx
import random
import time
import threading


class SortingFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Sorting Algorithms Visualization")
        self.SetSize((1000, 600))  # Set the initial window size
        self.Center()  # Center the window on the screen

        self.sorting_thread = None
        self.speed = None
        self.algorithm = None
        self.algorithm_name = None
        self.numbers = None
        self.initial_numbers = None
        self.completed = 0

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
        self.size_textbox = wx.TextCtrl(self.panel, value="", style=wx.TE_PROCESS_ENTER)
        self.random_size_slider = wx.Slider(self.panel, value=100, minValue=10, maxValue=500, style=wx.SL_HORIZONTAL)

        # Speed option
        self.speed_label = wx.StaticText(self.panel, label="Speed:")
        self.speed_slider = wx.Slider(self.panel, value=50, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL)

        # Sorting algorithms list box
        self.algorithms_radiobox = wx.RadioBox(self.panel, choices=list(self.algorithms.keys()), style=wx.RA_SPECIFY_ROWS)

        # Graph types radio buttons
        self.graph_type_label = wx.StaticText(self.panel, label="Graph Type:")
        self.graph_type_radiobox = wx.RadioBox(self.panel, choices=["Scatter Chart", "Column (Bar) Graph", "Stem Graph"],
                                               style=wx.RA_SPECIFY_ROWS)

        # Create, Start, Stop, Reset buttons
        self.button_create = wx.Button(self.panel, wx.ID_ANY, "Create")
        self.button_start = wx.Button(self.panel, wx.ID_ANY, "Start")
        self.button_stop = wx.Button(self.panel, wx.ID_ANY, "Stop")
        self.button_reset = wx.Button(self.panel, wx.ID_ANY, "Reset")

        # Bind event handlers
        self.Bind(wx.EVT_BUTTON, self.on_create, self.button_create)
        self.Bind(wx.EVT_BUTTON, self.on_start, self.button_start)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        self.Bind(wx.EVT_BUTTON, self.on_reset, self.button_reset)
        self.size_textbox.Bind(wx.EVT_TEXT_ENTER, self.on_create)

        # Sizer for left side elements
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.size_label, 0, wx.ALL, 5)
        left_sizer.Add(self.size_textbox, 0, wx.EXPAND | wx.ALL, 5)
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

        # Main sizer for the frame
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(left_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.graph_panel, 1, wx.EXPAND | wx.ALL, 10)

        # Activate or Disable buttons accordingly
        self.button_create.Enable()
        self.button_start.Disable()
        self.button_stop.Disable()
        self.button_reset.Disable()

        self.panel.SetSizer(main_sizer)
        self.Layout()

    def on_create(self, event):
        size_text = self.size_textbox.GetValue()
        graph_type = self.graph_type_radiobox.GetStringSelection()

        if size_text:
            try:
                size = int(size_text)
                if size < 1:
                    wx.MessageBox("Invalid size!", "Error", wx.OK | wx.ICON_ERROR)
                    return
                self.numbers = random.sample(range(1, size + 1), size)
            except ValueError:
                wx.MessageBox("Invalid size input!", "Error", wx.OK | wx.ICON_ERROR)
                return
        else:
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
        self.size_textbox.Disable()

        self.initial_numbers = self.numbers
        self.sorting_thread = threading.Thread(target=self.algorithm, args=(self.speed,))
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
        self.size_textbox.Disable()

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
        self.size_textbox.Disable()

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
        self.size_textbox.Enable()

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
        self.size_textbox.Enable()

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
                self.graph_panel.set_highlighted_indices([j, j + 1])
                self.graph_panel.Refresh()
                time.sleep(speed)
                self.graph_panel.set_numbers(numbers)
                j -= 1

                if self.state == 3:
                    self.numbers = numbers
                    return

            numbers[j + 1] = key
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

                for j in range(n2):
                    R[j] = arr[m + 1 + j]

                i = j = 0
                k = l

                while i < n1 and j < n2:
                    if L[i] <= R[j]:
                        arr[k] = L[i]
                        i += 1
                    else:
                        arr[k] = R[j]
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
                    i += 1
                    k += 1

                while j < n2:
                    arr[k] = R[j]
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
                i = (low - 1)
                pivot = arr[high]

                for j in range(low, high):
                    if arr[j] <= pivot:
                        i = i + 1
                        arr[i], arr[j] = arr[j], arr[i]
                        self.graph_panel.set_highlighted_indices([i, high, low, j])  # Highlight subarrays
                        self.graph_panel.set_numbers(arr)
                        time.sleep(speed)

                    if self.state == 3:
                        self.numbers = arr
                        return -1

                arr[i + 1], arr[high] = arr[high], arr[i + 1]
                return (i + 1)

            def quick_sort_helper(arr, low, high):
                if low < high:
                    pi = partition(arr, low, high)
                    if pi == -1:
                        return
                    quick_sort_helper(arr, low, pi - 1)
                    quick_sort_helper(arr, pi + 1, high)
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

        self.Bind(wx.EVT_PAINT, self.on_paint)

    def set_numbers(self, numbers):
        self.numbers = numbers
        self.Refresh()

    def set_highlighted_indices(self, indices):
        self.highlighted_indices = indices
        self.Refresh()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()

        width, height = self.GetSize()

        if not self.numbers:  # Check if the numbers list is empty
            return

        bar_width = width // len(self.numbers)
        max_height = max(self.numbers)

        # Handle the case when max_height is zero
        if max_height == 0:
            max_height = 1

        for i, num in enumerate(self.numbers):
            x = i * bar_width
            bar_height = int((num / max_height) * (height - 20))  # Convert to integer

            # Set color based on highlighted indices
            if i in self.highlighted_indices:
                dc.SetBrush(wx.Brush(wx.RED))  # Highlighted color
            else:
                dc.SetBrush(wx.Brush(wx.BLUE))  # Default color

            dc.DrawRectangle(x, height - bar_height, bar_width, bar_height)

    def reset_graph(self):
        self.numbers = []  # Clear the numbers list
        self.highlighted_indices = []  # Clear the highlighted indices
        self.Refresh()  # Refresh the panel to clear the graph

    def set_graph_type(self, graph_type):
        self.graph_type = graph_type
        self.Refresh()  # Refresh the panel to update the graph type

app = wx.App()
frame = SortingFrame()
frame.Show()
app.MainLoop()