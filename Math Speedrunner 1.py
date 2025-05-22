import random
import sys
import os

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QLabel, QLineEdit, QTextEdit, QStackedWidget, QScrollArea
)
from PyQt5.QtGui import QFont, QPixmap

IMAGE_DIR = r"C:\Users\s2008\OneDrive"

APP_COLORS = {
    "bg":      "#121212",
    "primary": "#BB86FC",
    "teal":    "#03DAC6",
    "panel":   "#1E1E1E",
    "text":    "#FFFFFF",
    "focus":   "#3700B3",
    "right":   "#4CAF50",
    "wrong":   "#CF6679",
    "warn":    "#FFC107",
    "alert":   "#FF5252"
}
class PracticeArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.host = parent
        self.setStyleSheet(f"background-color: {APP_COLORS['bg']};")
        layout = QVBoxLayout(self)

        # Option Selects
        options_container = QWidget()
        options_container.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; padding: 12px; border-radius: 8px; max-height: 80px;"
        )
        options_layout = QHBoxLayout(options_container)

        # Selection Option
        self.op_label = QLabel("Operation:")
        self.op_label.setStyleSheet(
            f"color: {APP_COLORS['text']}; font-size: 16px; font-weight: bold; font-family: 'Comic Sans MS', Arial;"
        )
        self.op_picker = QComboBox()
        self.op_picker.addItems(["Addition", "Subtraction", "Multiplication", "Division"])
        self.op_picker.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; color: {APP_COLORS['text']}; font-size: 14px;"
            f"padding: 8px; border-radius: 5px; min-width: 100px; font-family: 'Comic Sans MS', Arial;"
        )

        self.range_label = QLabel("Digits:")
        self.range_label.setStyleSheet(
            f"color: {APP_COLORS['text']}; font-size: 16px; font-weight: bold; font-family: 'Comic Sans MS', Arial;"
        )
        self.range_picker = QComboBox()
        self.range_picker.addItems(["1-Digit", "2-Digit", "3-Digit"])
        self.range_picker.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; color: {APP_COLORS['text']}; font-size: 14px; "
            f"padding: 8px; border-radius: 5px; min-width: 100px; font-family: 'Comic Sans MS', Arial;"
        )

        for w in [self.op_label, self.op_picker, self.range_label, self.range_picker]:
            options_layout.addWidget(w)

        layout.addWidget(options_container)

        # Start Game Button
        self.play_button = QPushButton("Start Game")
        self.play_button.setStyleSheet(
            f"background-color: {APP_COLORS['primary']}; color: {APP_COLORS['text']}; font-weight: bold; "
            "padding: 10px; font-size: 26px; border-radius: 5px; min-width: 150px; font-family: 'Comic Sans MS', Arial;"
        )
        self.play_button.clicked.connect(self.begin_game)
        layout.addWidget(self.play_button, alignment=Qt.AlignCenter)

        # Game Interaction Zone
        interaction_zone = QWidget()
        interaction_zone.setStyleSheet(f"background-color: {APP_COLORS['panel']}; padding: 15px; border-radius: 5px;")
        zone_layout = QVBoxLayout(interaction_zone)

        self.puzzle_text = QLabel("Pick options and start!")
        self.puzzle_text.setFont(QFont("Arial", 16, QFont.Bold))
        self.puzzle_text.setStyleSheet(f"color: {APP_COLORS['text']}; padding: 5px; font-family: 'Comic Sans MS', Arial;")
        self.puzzle_text.setAlignment(Qt.AlignCenter)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter your answer here...")
        self.input_field.setStyleSheet(
            f"background-color: {APP_COLORS['bg']}; color: {APP_COLORS['text']}; padding: 8px; font-size: 14px; border-radius: 3px; font-family: 'Comic Sans MS', Arial;"
        )
        self.input_field.setEnabled(False)
        self.input_field.returnPressed.connect(self.validate_answer)

        zone_layout.addWidget(self.puzzle_text)
        zone_layout.addWidget(self.input_field)

        # Info Bar (Timer + Score)
        bar = QWidget()
        bar_layout = QHBoxLayout(bar)
        self.time_left = QLabel("Time: 60")
        self.points = QLabel("Score: 0")

        for lbl in [self.time_left, self.points]:
            lbl.setStyleSheet(
                f"color: {APP_COLORS['text']}; font-weight: bold; font-size: 14px; background-color: {APP_COLORS['focus']}; padding: 5px; border-radius: 3px; font-family: 'Comic Sans MS', Arial;"
            )

        bar_layout.addWidget(self.time_left)
        bar_layout.addStretch()
        bar_layout.addWidget(self.points)
        zone_layout.addWidget(bar)

        layout.addWidget(interaction_zone)

        # High score
        self.best = 0
        self.best_display = QLabel("High Score: 0")
        self.best_display.setStyleSheet(
            f"color: {APP_COLORS['primary']}; font-size: 14px; font-weight: bold; "
            f"background-color: {APP_COLORS['panel']}; padding: 3px; border-radius: 3px; max-height: 20px; font-family: 'Comic Sans MS', Arial;"
        )
        layout.addWidget(self.best_display)

        # Return to Menu
        self.back = QPushButton("Back to Menu")
        self.back.setStyleSheet(
            f"background-color: {APP_COLORS['teal']}; color: {APP_COLORS['bg']}; font-weight: bold; padding: 8px; border-radius: 5px; font-family: 'Comic Sans MS', Arial;"
        )
        self.back.clicked.connect(lambda: parent.switch_screen(0))
        layout.addWidget(self.back, alignment=Qt.AlignCenter)

        # Runtime State Vars
        self.score = 0
        self.seconds = 60
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.right_ans = None
        self.mode = ""
        self.range = ""

    def begin_game(self):
        self.score, self.seconds = 0, 60
        self.update_labels()

        self.mode = self.op_picker.currentText()
        self.range = self.range_picker.currentText()

        self.play_button.setEnabled(False)
        self.op_picker.setEnabled(False)
        self.range_picker.setEnabled(False)

        self.input_field.setEnabled(True)
        self.input_field.clear()
        self.input_field.setFocus()

        self.timer.start(1000)
        self.make_question()

    def make_question(self):
        if self.range == "1-Digit":
            limit = 9
        elif self.range == "2-Digit":
            limit = 99
        else:
            limit = 999

        a = random.randint(1, limit)
        b = random.randint(1, limit)

        if self.mode == "Division":
            a = a * b if b != 0 else a + 1

        if self.mode == "Addition":
            self.puzzle_text.setText(f"{a} + {b} = ?")
            self.right_ans = a + b
        elif self.mode == "Subtraction":
            self.puzzle_text.setText(f"{max(a, b)} - {min(a, b)} = ?")
            self.right_ans = abs(a - b)
        elif self.mode == "Multiplication":
            self.puzzle_text.setText(f"{a} × {b} = ?")
            self.right_ans = a * b
        elif self.mode == "Division":
            self.puzzle_text.setText(f"{a} ÷ {b} = ?")
            self.right_ans = a // b if b != 0 else 0

    def validate_answer(self):
        if not self.input_field.isEnabled():
            return

        try:
            response = int(self.input_field.text())
        except ValueError:
            response = None

        if response == self.right_ans:
            self.score += 10
            self.puzzle_text.setStyleSheet(f"color: {APP_COLORS['right']}; padding: 5px;")
        else:
            self.score -= 5
            self.puzzle_text.setStyleSheet(f"color: {APP_COLORS['wrong']}; padding: 5px;")

        self.input_field.clear()
        self.update_labels()
        self.make_question()
        self.puzzle_text.setStyleSheet(f"color: {APP_COLORS['text']}; padding: 5px;")

    def tick(self):
        self.seconds -= 1
        self.update_labels()

        if self.seconds <= 10:
            color = APP_COLORS['warn'] if self.seconds > 5 else APP_COLORS['alert']
            self.time_left.setStyleSheet(
                f"color: {color}; font-weight: bold; font-size: 14px; background-color: {APP_COLORS['focus']}; padding: 5px; border-radius: 3px; font-family: 'Comic Sans MS', Arial;"
            )

        if self.seconds <= 0:
            self.timer.stop()
            self.input_field.setEnabled(False)
            self.play_button.setEnabled(True)
            self.op_picker.setEnabled(True)
            self.range_picker.setEnabled(True)

            if self.score > self.best:
                self.best = self.score
                self.best_display.setText(f"High Score: {self.best}")

            record_key = f"{self.mode}_{self.range}"
            if self.score > self.host.high_scores.get(record_key, 0):
                self.host.high_scores[record_key] = self.score

            self.puzzle_text.setText(f"Time's up! Final Score: {self.score}")
            self.puzzle_text.setStyleSheet(f"color: {APP_COLORS['wrong']}; padding: 5px; font-family: 'Comic Sans MS', Arial;")

    def update_labels(self):
        self.time_left.setText(f"Time: {self.seconds}")
        self.points.setText(f"Score: {self.score}")


class HighScoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet(f"background-color: {APP_COLORS['bg']};")
        layout = QVBoxLayout(self)

        self.title = QLabel("High Scores")
        self.title.setStyleSheet(
            f"color: {APP_COLORS['primary']}; font-weight: bold; font-size: 24px; font-family: 'Comic Sans MS', Arial;")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.scores_display = QTextEdit()
        self.scores_display.setReadOnly(True)
        self.scores_display.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; color: {APP_COLORS['text']}; font-size: 14px; border: none; font-family: 'Comic Sans MS', Arial;")
        layout.addWidget(self.scores_display)

        back_button = QPushButton("Back to Menu")
        back_button.setStyleSheet(
            f"background-color: {APP_COLORS['teal']}; color: {APP_COLORS['bg']}; font-weight: bold; padding: 8px; border-radius: 5px; font-family: 'Comic Sans MS', Arial;")
        back_button.clicked.connect(lambda: parent.switch_screen(0))
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

    def update_scores(self):
        scores_text = "High Scores:\n\n"
        for key, value in self.parent.high_scores.items():
            scores_text += f"{key}: {value}\n"
        self.scores_display.setText(scores_text)


class LearnWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet(f"background-color: {APP_COLORS['bg']};")
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Learn Math Tricks")
        title.setStyleSheet(
            f"color: {APP_COLORS['primary']}; font-weight: bold; font-size: 24px; font-family: 'Comic Sans MS', Arial;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Selection area
        selection_box = QWidget()
        selection_box.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; padding: 10px; border-radius: 5px;")
        selection_layout = QHBoxLayout(selection_box)

        self.operation_label = QLabel("Operation:")
        self.operation_label.setStyleSheet(f"color: {APP_COLORS['text']}; font-weight: bold; font-family: 'Comic Sans MS', Arial;")

        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["Addition", "Subtraction", "Multiplication"])
        self.operation_combo.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; color: {APP_COLORS['text']};"
            "padding: 5px; border-radius: 3px; min-width: 120px; font-family: 'Comic Sans MS', Arial;")

        self.digit_label = QLabel("Number Range:")
        self.digit_label.setStyleSheet(f"color: {APP_COLORS['text']}; font-weight: bold; font-family: 'Comic Sans MS', Arial;")

        self.digit_combo = QComboBox()
        self.digit_combo.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; color: {APP_COLORS['text']};"
            "padding: 5px; border-radius: 3px; min-width: 120px;")

        # Initialize digit options based on default operation
        self.update_digit_options()

        selection_layout.addWidget(self.operation_label)
        selection_layout.addWidget(self.operation_combo)
        selection_layout.addWidget(self.digit_label)
        selection_layout.addWidget(self.digit_combo)
        layout.addWidget(selection_box)

        # Slideshow area
        content_box = QWidget()
        content_box.setStyleSheet(
            f"background-color: {APP_COLORS['panel']}; padding: 1px; border-radius: 1px;")
        content_layout = QVBoxLayout(content_box)
        content_layout.setAlignment(Qt.AlignCenter)

        # Add slides_stack to a QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            f"""
                            QScrollArea {{
                                background-color: {APP_COLORS['focus']}; 
                                border: none;
                            }}
                            QScrollBar:vertical {{
                                border: none;
                                background: {APP_COLORS['bg']};
                                width: 10px;
                                margin: 0px 0px 0px 0px;
                            }}
                            QScrollBar::handle:vertical {{
                                background: #FFFFFF;
                                min-height: 20px;
                                border-radius: 5px;
                            }}
                            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                                background: {APP_COLORS['bg']};
                                height: 0px;
                            }}
                            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                                background: {APP_COLORS['bg']};
                            }}
                            QScrollBar:horizontal {{
                                border: none;
                                background: {APP_COLORS['bg']};
                                height: 10px;
                                margin: 0px 0px 0px 0px;
                            }}
                            QScrollBar::handle:horizontal {{
                                background: #FFFFFF;
                                min-width: 20px;
                                border-radius: 5px;
                            }}
                            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                                background: {APP_COLORS['bg']};
                                width: 0px;
                            }}
                            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                                background: {APP_COLORS['bg']};
                            }}
                            """
        )

        # Add slides_stack directly to content_layout
        self.slides_stack = QStackedWidget()
        self.slides_stack.setStyleSheet(
            f"background-color: {APP_COLORS['bg']};")
        self.scroll_area.setWidget(self.slides_stack)
        content_layout.addWidget(self.scroll_area)

        # Navigation buttons with slide indicator
        nav_box = QWidget()
        nav_layout = QHBoxLayout(nav_box)
        self.prev_button = QPushButton("Previous")
        self.prev_button.setStyleSheet(
            f"background-color: {APP_COLORS['teal']}; color: {APP_COLORS['text']}; "
            "font-weight: bold; padding: 8px; border-radius: 5px; font-family: 'Comic Sans MS', Arial;")
        self.prev_button.clicked.connect(self.show_prev_slide)
        self.prev_button.setEnabled(False)

        # Slide indicator
        self.slide_indicator = QLabel("•")
        self.slide_indicator.setStyleSheet(
            f"color: {APP_COLORS['text']}; font-size: 16px; font-weight: bold;")

        self.next_button = QPushButton("Next")
        self.next_button.setStyleSheet(
            f"background-color: {APP_COLORS['teal']}; color: {APP_COLORS['text']}; "
            "font-weight: bold; padding: 8px; border-radius: 5px; font-family: 'Comic Sans MS', Arial;")
        self.next_button.clicked.connect(self.show_next_slide)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.slide_indicator)
        nav_layout.addWidget(self.next_button)
        content_layout.addWidget(nav_box, alignment=Qt.AlignCenter)

        layout.addWidget(content_box)

        # Back button
        back_button = QPushButton("Back to Menu")
        back_button.setStyleSheet(
            f"background-color: {APP_COLORS['teal']}; color: {APP_COLORS['bg']}; "
            "font-weight: bold; padding: 8px; border-radius: 5px;")
        back_button.clicked.connect(lambda: parent.switch_screen(0))
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        # Initialize slides
        self.current_slides = []
        self.operation_combo.currentTextChanged.connect(self.update_digit_options)
        self.operation_combo.currentTextChanged.connect(self.update_slides)
        self.digit_combo.currentTextChanged.connect(self.update_slides)
        self.update_slides()

    def update_digit_options(self):
        current_operation = self.operation_combo.currentText()
        self.digit_combo.clear()

        if current_operation in ["Addition", "Subtraction"]:
            self.digit_combo.addItems(["2-Digit", "2-3-Digit", "3-Digit"])
        else:
            self.digit_combo.addItems(["2-Digit", "3-Digit"])

    def create_slide(self, image_path=None, message=None):
        slide = QWidget()
        slide_layout = QVBoxLayout(slide)
        slide_layout.setAlignment(Qt.AlignCenter)
        slide_layout.setContentsMargins(0, 0, 0, 0)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet(f"background-color: {APP_COLORS['bg']};")

        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                available_width = min(self.parent.width() - 40, 700)
                available_height = min(self.parent.height() - 150, 900)
                scaled_pixmap = pixmap.scaled(
                    available_width,
                    available_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                image_label.setPixmap(scaled_pixmap)
                image_label.setFixedSize(scaled_pixmap.size())
            else:
                image_label.setText(f"Image not found: {image_path}")
                print(f"Warning: Failed to load image at {image_path}")
        elif message:
            image_label.setText(message)
            image_label.setStyleSheet(f"color: {APP_COLORS['text']}; font-size: 16px; font-family: 'Comic Sans MS', Arial;")

        slide_layout.addWidget(image_label, alignment=Qt.AlignCenter)
        slide_layout.addStretch()
        return slide

    def update_slide_indicator(self):
        current_index = self.slides_stack.currentIndex()
        total_slides = len(self.current_slides)
        if total_slides == 0:
            self.slide_indicator.setText("")
            return
        # Create dot representation: filled (•) for current and previous, unfilled (○) for upcoming
        dots = ["•" if i <= current_index else "○" for i in range(total_slides)]
        self.slide_indicator.setText(" ".join(dots))

    def update_slides(self):
        operation = self.operation_combo.currentText()
        digit = self.digit_combo.currentText()

        while self.slides_stack.count() > 0:
            widget = self.slides_stack.widget(0)
            self.slides_stack.removeWidget(widget)
            widget.deleteLater()
        self.current_slides = []

        image_paths = []

        if operation == "Addition":
            if digit == "2-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Addition", f"Slide{i}.JPG") for i in range(1, 6)
                ]
            elif digit == "2-3-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Addition", f"Slide{i}.JPG") for i in range(6, 11)
                ]
            elif digit == "3-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Addition", f"Slide{i}.JPG") for i in range(11, 16)
                ]

        elif operation == "Subtraction":
            if digit == "2-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Subtraction", f"Slide{i}.JPG") for i in range(1, 6)
                ]
            elif digit == "2-3-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Subtraction", f"Slide{i}.JPG") for i in range(6, 11)
                ]
            elif digit == "3-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Subtraction", f"Slide{i}.JPG") for i in range(11, 16)
                ]

        elif operation == "Multiplication":
            if digit == "2-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Multiplication", f"Slide{i}.JPG") for i in range(1, 11)
                ]
            elif digit == "3-Digit":
                image_paths = [
                    os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Multiplication", f"Slide{i}.JPG") for i in range(11, 25)
                ]

        else:
            slide = self.create_slide(message=f"No slides available for {operation}")
            self.slides_stack.addWidget(slide)
            self.current_slides.append(slide)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.update_slide_indicator()
            return

        for path in image_paths:
            slide = self.create_slide(image_path=path)
            self.slides_stack.addWidget(slide)
            self.current_slides.append(slide)

        self.slides_stack.setCurrentIndex(0)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(len(self.current_slides) > 1)
        self.update_slide_indicator()

    def show_prev_slide(self):
        current_index = self.slides_stack.currentIndex()
        if current_index > 0:
            self.slides_stack.setCurrentIndex(current_index - 1)
            self.next_button.setEnabled(True)
            if current_index - 1 == 0:
                self.prev_button.setEnabled(False)
            self.update_slide_indicator()

    def show_next_slide(self):
        current_index = self.slides_stack.currentIndex()
        if current_index < len(self.current_slides) - 1:
            self.slides_stack.setCurrentIndex(current_index + 1)
            self.prev_button.setEnabled(True)
            if current_index + 1 == len(self.current_slides) - 1:
                self.next_button.setEnabled(False)
            self.update_slide_indicator()

    def resizeEvent(self, event):
        # Avoid resizing images in resizeEvent to prevent loops
        super().resizeEvent(event)


# Main Application Window
class MathsSpeedrunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maths Speedrunner")
        self.setGeometry(100, 100, 700, 900)

        # Central widget with stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"background-color: {APP_COLORS['bg']};")

        self.layout = QVBoxLayout(self.central_widget)

        # Shared high scores
        self.high_scores = {}

        # Stacked widget for screen switching
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        # Main menu
        self.main_menu = QWidget()
        self.main_menu.setStyleSheet(f"""
            background-image: url("{os.path.join(IMAGE_DIR, 'Pictures', 'Math SpeedRunner', 'Background1.png')}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        """)
        main_layout = QVBoxLayout(self.main_menu)

        # Add image to main menu
        image_label = QLabel()
        pixmap = QPixmap(os.path.join(IMAGE_DIR, "Pictures", "Math SpeedRunner", "Math SpeedRunner.png"))
        if not pixmap.isNull():
            available_width = min(self.width() - 40, 600)
            available_height = min(self.height() - 300, 400)
            scaled_pixmap = pixmap.scaled(
                available_width, available_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
        else:
            image_label.setText("Failed to load image")
            image_label.setStyleSheet(f"color: {APP_COLORS['alert']}; font-size: 16px; font-family: 'Comic Sans MS', Arial;")
        main_layout.addWidget(image_label, alignment=Qt.AlignCenter)

        practice_button = QPushButton("Practice")
        practice_button.setStyleSheet(
            "background-color: #32cd32; color: white; font-weight: bold; padding: 10px; font-size: 16px; border-radius: 5px; font-family: 'Comic Sans MS', Arial;")
        practice_button.clicked.connect(lambda: self.switch_screen(1))
        main_layout.addWidget(practice_button)

        learn_button = QPushButton("Learn")
        learn_button.setStyleSheet(
            "background-color: #ff4500; color: white; font-weight: bold; padding: 10px; font-size: 16px; border-radius: 5px; font-family: 'Comic Sans MS', Arial;")
        learn_button.clicked.connect(lambda: self.switch_screen(2))
        main_layout.addWidget(learn_button)

        high_scores_button = QPushButton("High Scores")
        high_scores_button.setStyleSheet(
            "background-color: #4b0082; color: white; font-weight: bold; padding: 10px; font-size: 16px; border-radius: 5px; font-family: 'Comic Sans MS', Arial;")
        high_scores_button.clicked.connect(lambda: self.switch_screen(3))
        main_layout.addWidget(high_scores_button)

        main_layout.addStretch()

        # Add widgets to stack
        self.stack.addWidget(self.main_menu)         # Index 0
        self.stack.addWidget(PracticeArea(self))     # Index 1
        self.stack.addWidget(LearnWidget(self))      # Index 2
        self.stack.addWidget(HighScoreWidget(self))  # Index 3

    def switch_screen(self, index):
        if index == 3:
            high_score_widget = self.stack.widget(3)
            high_score_widget.update_scores()
        self.stack.setCurrentIndex(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MathsSpeedrunner()
    window.show()
    sys.exit(app.exec_())
