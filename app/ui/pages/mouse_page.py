"""Mouse Clicker page — UI layout only; wired to worker/thread logic separately."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import ClickMode, MouseButtonOption
from app.ui.widgets import PageHeader, StatusIndicator


class MousePage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(14)

        root.addWidget(
            PageHeader(
                "Mouse Clicker",
                "Automate clicks at your cursor, a fixed point, or a sequence of points.",
            )
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        root.addLayout(grid, 1)

        grid.addWidget(self._build_click_settings_group(), 0, 0)
        grid.addWidget(self._build_interval_group(), 1, 0)
        grid.addWidget(self._build_position_group(), 0, 1, 2, 1)
        grid.addWidget(self._build_limit_group(), 2, 0, 1, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        root.addLayout(self._build_control_bar())

    # ---- groups -----------------------------------------------------

    def _build_click_settings_group(self) -> QGroupBox:
        box = QGroupBox("Click Settings")
        form = QFormLayout(box)
        form.setSpacing(10)

        self.button_combo = QComboBox()
        for opt in MouseButtonOption:
            self.button_combo.addItem(opt.value, opt)

        self.mode_combo = QComboBox()
        for mode in ClickMode:
            self.mode_combo.addItem(mode.value, mode)

        form.addRow("Button:", self.button_combo)
        form.addRow("Click mode:", self.mode_combo)
        return box

    def _build_interval_group(self) -> QGroupBox:
        box = QGroupBox("Interval")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        row = QHBoxLayout()
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.001, 3_600_000)
        self.interval_spin.setDecimals(3)
        self.interval_spin.setValue(100)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["ms", "s"])
        row.addWidget(QLabel("Every:"))
        row.addWidget(self.interval_spin, 1)
        row.addWidget(self.unit_combo)
        layout.addLayout(row)

        self.random_check = QCheckBox("Randomize delay")
        layout.addWidget(self.random_check)

        random_row = QHBoxLayout()
        self.random_min_spin = QDoubleSpinBox()
        self.random_min_spin.setRange(0, 3_600_000)
        self.random_min_spin.setValue(50)
        self.random_max_spin = QDoubleSpinBox()
        self.random_max_spin.setRange(0, 3_600_000)
        self.random_max_spin.setValue(150)
        random_row.addWidget(QLabel("Min:"))
        random_row.addWidget(self.random_min_spin)
        random_row.addWidget(QLabel("Max:"))
        random_row.addWidget(self.random_max_spin)
        layout.addLayout(random_row)

        self.random_min_spin.setEnabled(False)
        self.random_max_spin.setEnabled(False)
        self.random_check.toggled.connect(self.random_min_spin.setEnabled)
        self.random_check.toggled.connect(self.random_max_spin.setEnabled)

        layout.addStretch(1)
        return box

    def _build_position_group(self) -> QGroupBox:
        box = QGroupBox("Click Position")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        self.pos_current_radio = QRadioButton("Current cursor position")
        self.pos_fixed_radio = QRadioButton("Fixed coordinates")
        self.pos_multi_radio = QRadioButton("Multiple points (multi-click)")

        self.position_group = QButtonGroup(box)
        for i, radio in enumerate(
            (self.pos_current_radio, self.pos_fixed_radio, self.pos_multi_radio)
        ):
            self.position_group.addButton(radio, i)
            layout.addWidget(radio)

        self.pos_current_radio.setChecked(True)

        self.position_stack = QStackedWidget()
        self.position_stack.addWidget(QWidget())  # current cursor: nothing to configure
        self.position_stack.addWidget(self._build_fixed_coords_panel())
        self.position_stack.addWidget(self._build_multi_points_panel())
        layout.addWidget(self.position_stack, 1)

        self.position_group.idClicked.connect(self.position_stack.setCurrentIndex)
        return box

    def _build_fixed_coords_panel(self) -> QWidget:
        panel = QWidget()
        form = QFormLayout(panel)
        form.setContentsMargins(20, 4, 0, 0)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 20000)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 20000)

        form.addRow("X:", self.x_spin)
        form.addRow("Y:", self.y_spin)

        self.pick_point_btn = QPushButton("Pick on Screen…")
        form.addRow("", self.pick_point_btn)
        return panel

    def _build_multi_points_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 4, 0, 0)
        layout.setSpacing(8)

        self.points_table = QTableWidget(0, 2)
        self.points_table.setHorizontalHeaderLabels(["X", "Y"])
        self.points_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.points_table.verticalHeader().setVisible(False)
        self.points_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.points_table.setMaximumHeight(140)
        layout.addWidget(self.points_table)

        btn_row = QHBoxLayout()
        self.add_point_btn = QPushButton("Add Point…")
        self.remove_point_btn = QPushButton("Remove Selected")
        self.clear_points_btn = QPushButton("Clear All")
        btn_row.addWidget(self.add_point_btn)
        btn_row.addWidget(self.remove_point_btn)
        btn_row.addWidget(self.clear_points_btn)
        layout.addLayout(btn_row)

        return panel

    def _build_limit_group(self) -> QGroupBox:
        box = QGroupBox("Limit && Options")
        layout = QHBoxLayout(box)
        layout.setSpacing(20)

        limit_col = QVBoxLayout()
        self.limit_infinite_radio = QRadioButton("Infinite")
        self.limit_fixed_radio = QRadioButton("Fixed count")
        self.limit_group = QButtonGroup(box)
        self.limit_group.addButton(self.limit_infinite_radio, 0)
        self.limit_group.addButton(self.limit_fixed_radio, 1)
        self.limit_infinite_radio.setChecked(True)

        fixed_row = QHBoxLayout()
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 10_000_000)
        self.limit_spin.setValue(100)
        self.limit_spin.setEnabled(False)
        self.limit_fixed_radio.toggled.connect(self.limit_spin.setEnabled)
        fixed_row.addWidget(self.limit_fixed_radio)
        fixed_row.addWidget(self.limit_spin)

        limit_col.addWidget(self.limit_infinite_radio)
        limit_col.addLayout(fixed_row)
        limit_col.addStretch(1)

        options_col = QVBoxLayout()
        self.return_cursor_check = QCheckBox("Return cursor to original position after click")
        options_col.addWidget(self.return_cursor_check)
        options_col.addStretch(1)

        layout.addLayout(limit_col, 1)
        layout.addLayout(options_col, 1)
        return box

    def _build_control_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setMinimumWidth(120)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("DangerButton")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setEnabled(False)

        self.status_indicator = StatusIndicator()
        self.count_label = QLabel("Clicks: 0")
        self.count_label.setStyleSheet("color: #9099a8;")

        bar.addWidget(self.start_btn)
        bar.addWidget(self.stop_btn)
        bar.addSpacing(12)
        bar.addWidget(self.status_indicator)
        bar.addStretch(1)
        bar.addWidget(self.count_label)
        return bar
